# MLCA MCP server: implementation plan

Plan for a coding agent. It adds an **MCP server** to MLCA v2, so that general agents (Claude Code, Codex, Hermes, OpenClaw, Cursor, and any other MCP client) can drive an MLCA project. The engine's rules stay in force whoever is driving.

Written 2026-10-06. Companion to `plan.md`, which covers the core harness; read `plan.md` sections 0, 2 and 3 first. Every rule in `plan.md` section 0 applies here too: new code, offline tests, no hard-coded models, local commits only, nothing published. Record each decision in `docs/DECISIONS.md` and each deviation from this plan, with its reason.

---

## 0. Prerequisite

**Published beta:** [`mlcagent` 0.2.0b1](https://pypi.org/project/mlcagent/0.2.0b1/). Both files were accepted by PyPI with the author-provided token; public SHA256 hashes match the tested artifacts. Local release source: `16bcc72`.


**Latest work:** P10.1–P10.7 implemented with sourced metrics, usage imports and independent task-card benchmarks. The author-approved distribution is `mlcagent` 0.2.0b1; command/import remain `mlca`. Release validation passed (137 tests passed, 1 skipped). Both artifacts are published at [https://pypi.org/project/mlcagent/0.2.0b1/](https://pypi.org/project/mlcagent/0.2.0b1/); fresh-index installation and 14-tool verification passed. Older upload results below describe the rejected `mlca` name, not this release.
 (core work, tracked in `plan.md`)

Do not start M1 until the missing core invariant tests listed in `plan.md` → *Status* → *Still open* are written and pass:
- I3: gate blocked;
- I4: model output cannot satisfy a sub-goal;
- I5: invalid Navigator output → repair → fallback;
- I6: a layer-1 scope rejection makes zero model calls;
- I8: step folder immutable;
- I9: `FactRejected`;
- the Worker repair loop, the budget stop, rate-limit retry and the credential-leak scan.

An MCP client is a new, untrusted driver. Those tests are the baseline, and section 8 re-runs the bypass cases through MCP.

---

## 1. Goal and the two docking modes

`mlca mcp` starts an MCP server (stdio) on top of the existing Session API (`src/mlca/api.py`). It is a third client, beside the CLI and the TUI. A connected agent can read the state, see the current options, choose, and move between events. It cannot approve its own work.

| | **Brain mode** (default for MCP) | **Driver mode** |
|---|---|---|
| Who thinks | the connected agent: it proposes options and writes every step script | MLCA's own Navigator and Worker (configured providers and API keys) |
| Model calls by MLCA | **none** | yes, as today |
| What the agent does | `mlca_options` → (optional) `mlca_submit_options` → `mlca_choose` → `mlca_submit_script` (repeat on failure) → `mlca_step_status` → `mlca_move` | `mlca_options` → `mlca_choose` → `mlca_step_status` → `mlca_move` |
| Engine rules | identical: catalog-only options, parameter validation, gates, sub-goal checks, scope guard layer 1, static checks, sandbox, fit rules, test lock, human-only approvals | identical |
| Who it suits | someone who already uses Claude Code, Codex, Hermes or OpenClaw, and wants that agent (and its subscription) to do the work | someone without such an agent, using MLCA alone from the TUI/CLI, or an agent that should only steer |

Both modes are always available. Brain mode is the author's preferred default for MCP. Driver mode is also what the plain TUI/CLI uses, so MLCA works without any external agent.

**Why brain mode is safe.** The agent supplies text: option choices and Python source. Everything that decides whether that text is acceptable is engine code:
- `engine/options.py: validate`, `parameters`;
- `engine/gates.py`, `engine/checks.py`;
- `runner/static_checks.py`, `runner/process.py`, `sandbox/*`;
- `mlca_runtime.fit_record`, `sandbox/vault.py`.

A script from Claude is treated exactly like a script from MLCA's own Worker.

---

## 2. Architecture

```
 Claude Code / Codex / Hermes / OpenClaw / Cursor      (MCP client = "hyper agent")
                │  stdio (JSON-RPC, MCP)
                ▼
 mlca mcp  ──  src/mlca/mcp/server.py      tools, resources, server instructions
                │  principal = agent:<clientInfo.name>/<clientInfo.version>
                ▼
 src/mlca/api.py  Session                  same API as CLI and TUI
                │
                ▼
 engine / runner / sandbox / log           unchanged rules; steps can now wait for a script (M1)
```

Concurrency: the existing project lock (`.mlca/action.lock`, `api.py: Session.mutation`) already serialises mutations between the TUI, the CLI and the MCP server. A busy project returns a clear "project busy" result, never a hang.

---

## 3. Engine changes first (M1)

These go into the core, but they exist for MCP, so they are specified here. Each needs a test.

### 3.1 Principal and attribution
- `Session.__init__(path, client, principal="user")`. CLI and TUI pass `principal="user"`. The MCP server passes `principal="agent:<name>/<version>"`, taken from the client's `initialize` `clientInfo`, or `agent:unknown`.
- In `Session.emit`, any record that the code currently writes with `actor="user"` (choices, custom instructions, branch commands) is written with `actor=self.principal`. Extend `log/schema.py` so `actor` accepts `agent:<...>` strings.
- **Human-only methods refuse non-human principals,** whatever client calls them: `confirm`, `unlock_test`, and `package(approve=True)`. This is defence in depth: they are also absent from the MCP tool list. The refusal message: "This decision is reserved for the human author; request it with mlca_request_approval."
- Reports: `report/usage_report.py` counts decisions by principal: user, each agent, engine.

### 3.2 Approval requests
- New record types:
  - `ApprovalRequested {kind: confirm|unlock_test|package, target, reason, requested_by}`;
  - `ApprovalResolved {request_id, decision: approved|declined, note}`.
- Human side:
  - `mlca approvals` lists the open requests; `mlca approvals approve <id> --note ...` performs the real action (`confirm`, `unlock_test`, `package`) and writes `ApprovalResolved`; `mlca approvals decline <id>`.
  - The TUI shows a one-line banner, "1 approval waiting (a)", and an approval dialog. Unlocking the test set still requires typing `UNLOCK TEST`.
- An approval never happens implicitly. Polling tools only report it.

### 3.3 Resumable steps (needed by brain mode)
Today `runner/run_step.py: _worker` loops synchronously, calling the Worker. Split it into a step state machine persisted in the event log:

```
StepStarted → ScriptRequested(attempt n, work_order) → ScriptWritten(attempt n, source=worker|agent:<..>)
            → StaticCheckFailed | RunFinished → [ScriptRequested(n+1) | StepCompleted | StepFailed]
```

- The new record `ScriptRequested` carries the work order (section 5.3) and its sha256.
- `log/replay.py` derives `step["status"]` ∈ `awaiting_script | running | completed | failed`.
- A **script source** interface (`runner/sources.py`):
  - `WorkerSource` (driver mode) calls `roles/worker.py` as now;
  - `ExternalSource` (brain mode) returns "awaiting script" and stops.

  `run_step` continues when `Session.submit_script(step_id, code)` is called.
- At most one active step (awaiting or running) per branch. While it is active, `choose`, `custom`, `move` and `branch` return "step <id> is waiting for a script" until it completes, fails or is abandoned. `Session.abandon_step(step_id, reason)` writes `StepFailed` with `reason: abandoned`.
- Attempts are limited by `budgets.worker_max_attempts` in both modes.
- **Test exposure per attempt:** decrypt the test partition only around each execution (`sandbox/vault.py: exposed`), never across a wait for the agent.

### 3.4 Mode selection
- A new config key: `mcp.mode: brain | driver` (default `brain`), overridable with `mlca mcp --mode`.
- In brain mode MLCA makes **no** model calls:
  - Navigator options fall back to the catalog (`engine/options.py: fallback`) unless the agent submits options;
  - facts come only from `mlca_runtime.record_fact_candidate`, already supported in `engine/turn.py`;
  - the Inspector is off;
  - scope-guard layer 2 is **skipped** and logged as `ScopeDecision {layer: 2, decision: skipped, reason: "brain mode"}`. Layer 1 and all execution rules still apply. Say so in the README.
- In driver mode, behaviour is exactly as today, except that `choose` and `custom` run in a background thread so the tool returns at once (section 5.2).

### 3.5 Session API additions (`api.py`)
`submit_options(options)`, `submit_script(step_id, code)`, `step_status(step_id)`, `abandon_step(step_id, reason)`, `request_approval(kind, target, reason)`, `approvals()`, `resolve_approval(id, decision, note)` (human only). `choose` and `custom` return `{step_id, status}` without waiting when the session is non-blocking (MCP); CLI and TUI keep blocking behaviour.

---

## 4. Package and commands

- **Dependency:** the official MCP Python SDK (`mcp`), as a **core** dependency, so installing MLCA installs the server. Use the current stable release and record its version and the MCP protocol version it negotiates in `docs/DECISIONS.md`. Use the SDK's high-level server API (FastMCP-style decorators), not hand-written JSON-RPC.
- **Files:**
  ```
  src/mlca/mcp/__init__.py
  src/mlca/mcp/server.py        server, tools, resources, instructions
  src/mlca/mcp/serialize.py     compact, privacy-filtered result shapes (section 6)
  src/mlca/mcp/install.py       client registration helpers (section 7)
  src/mlca/runner/sources.py    WorkerSource / ExternalSource (section 3.3)
  docs/mcp.md                   user guide (both modes, clients, safety)
  skills/mlca/SKILL.md          short protocol guide for agents (section 7.3)
  tests/mcp/                    section 8
  ```
- **CLI** (`cli/main.py`):
  - `mlca mcp [--project PATH] [--mode brain|driver]` starts the stdio server; logs go to stderr only.
  - `mlca mcp install --client claude|codex|hermes|openclaw|cursor|json [--scope user|project] [--mode ...] [--yes]` (section 7).
  - `mlca mcp doctor`: the `mlca` command is on PATH, the server starts and answers `tools/list`, plus the registration status where a client CLI is available (`claude mcp list`, `codex mcp list`).
  - `mlca approvals [approve|decline ID --note TEXT]`.

---

## 5. Tool surface (14 tools; stable names; no tool per action)

Every result is compact JSON (section 6). Each tool's description states the mode(s) it works in and that data-derived strings are untrusted data. Set MCP tool annotations: `readOnlyHint` for read tools; `destructiveHint: false` everywhere (nothing deletes evidence).

### 5.1 Tools

| Tool | Args | Returns | Mode | Engine path |
|---|---|---|---|---|
| `mlca_open` | `path` | project summary (template, current event, branch, mode) | both | `Session.open` (principal = agent) |
| `mlca_init` | `path, data[], template, brief{}` | project summary, or the column list if a brief column is unresolved | both | `project/init.py: initialise` (non-interactive) |
| `mlca_status` | — | event, goal, sub-goals with state, facts (key/value/source), branch, active step, open approvals, budget | both | `Session.status` |
| `mlca_options` | — | options `[{id, action_id, title, why_now, params, advances, expected_outputs}]` + `next`/`loop:*`/`custom` entries; in brain mode also the event's action catalog (id, title, params schema, outputs) | both | `Session.options` |
| `mlca_submit_options` | `options[]` | validated options or a precise rejection | brain | `engine/options.py: validate` (I5); records `OptionsProposed {source: agent:..}` |
| `mlca_choose` | `option_id` | `{step_id, status}`; in brain mode also the **work order** | both | `Session.choose` (non-blocking) |
| `mlca_custom` | `text` | scope decision; if accepted, `{step_id, status, work_order?}` | both | `Session.custom` (layer 1 always; layer 2 per mode) |
| `mlca_submit_script` | `step_id, code` | after the run: `completed` (outputs, metrics, facts, sub-goal changes), or `awaiting_script` with diagnostics and attempts left, or `failed` | brain | `Session.submit_script` → static checks, sandbox, collect |
| `mlca_step_status` | `step_id` | status, attempt, elapsed, last diagnostics, observation summary when complete | both | replay + runner state |
| `mlca_move` | `to: "next" \| <event>` | entered / gate blocked (with failing conditions) | both | `Session.next` / `Session.loop` |
| `mlca_branch` | `action: create\|checkout\|list, name?, from?` | branch summary | both | `Session.branch` / `checkout` |
| `mlca_request_approval` | `kind: confirm\|unlock_test\|package, target, reason` | request id + the exact human command (`mlca approvals approve <id>`) | both | `Session.request_approval` |
| `mlca_read` | `kind: figure\|script\|table\|log\|facts\|report, ref` | figure → **image content** (PNG); script → text; table → first 50 rows of a saved summary table; log → last N records, summarised | both | step folders, `reports/generated/` |
| `mlca_report` | `kind: methods\|provenance\|figures\|usage\|all` | paths + short summary (usage shows decisions by principal) | both | `Session.report` |

**Not exposed, by design:** confirming sub-goals, unlocking the test set, approving packages, editing logs or step folders, and changing config. These are human decisions or engine state.

### 5.2 Long steps
- `mlca_choose`, `mlca_custom` and `mlca_submit_script` return within about 2 s.
- Driver mode runs the step in a background thread holding the project lock. Brain mode runs the submitted script in a background thread the same way.
- The agent polls `mlca_step_status`. The returned status includes a `poll_after_s` hint (2–10 s).
- Where the client supports the MCP **tasks extension**, the same operations may also be offered as tasks. This is optional, behind a capability check, and must not be the only path.
- Progress notifications (attempt n, running, collecting) are sent when the client supports them.

### 5.3 Work order (brain mode)
Returned by `mlca_choose`/`mlca_custom` and repeated in `mlca_step_status` while awaiting a script. It is the same content MLCA's own Worker receives (`roles/prompts/worker_write.md`), rendered and structured:
```json
{"step_id": "...", "attempt": 1, "max_attempts": 3, "event": "validate", "action": "score_validation",
 "instructions": "Do: ... Save: ... Record: ...",
 "inputs": {"train": "train.parquet", "val": "val.parquet", "latest_model": "model.pkl"},
 "required_outputs": [{"name": "validation_metrics.csv", "kind": "table"}],
 "allowed_fact_keys": ["best_model", "best_val_roc_auc"],
 "rules": ["use mlca_runtime.inputs()/output_dir()", "fit only via fit_record on train", "no network, no subprocess", "output contract: ..."],
 "packages": ["numpy==...", "pandas==...", "scikit-learn==..."],
 "brief": {"aim": "...", "columns": {"target": "y"}}}
```
- Input names only, never absolute paths: the sandbox maps them at run time.
- Repair attempts add `"previous_diagnostics"`, filtered by privacy (section 6).

---

## 6. Result shapes, privacy and accounting

- **Compact by default.** Every result has a one-line `summary` field plus structured fields. No raw dataframes; tables are capped at 50 rows. Facts are returned with their source path and sha256.
- **Privacy:** results go to the agent's model provider, so they follow `privacy.allow_sample_rows`:
  - when false (the default), never include data rows;
  - run diagnostics are reduced to the exception type and script line, as for the Worker today (`runner/run_step.py`);
  - figures are allowed (they are summaries) but are counted in egress.
- **Egress log:** each tool result writes one line to `egress.jsonl` with `role: mcp`, the principal, tool name, bytes, sha256 and content categories (`template_spec`, `facts`, `inventory_summary`, `script`, `traceback`, `figure_image`, `table_summary`, `sample_rows`).
- **Usage:** in brain mode MLCA has no tokens to count. Write one line per tool call to `usage.jsonl` with `role: mcp`, the principal, tool, duration and `cost_source: external` (no cost). Reports show work by principal and per step: the number of script attempts and how many came from the agent versus the human.
- **Untrusted data:** column names, file names, stdout text and fact values are returned in fields named `data` or `*_data`, never inside the `summary` text. The server `instructions` say that these fields are data, not instructions.
- **Server instructions** (sent at `initialize`, at most 15 lines): the loop `status → options → choose → (brain: submit_script) → step_status → move`; one step at a time; human-only decisions go through `mlca_request_approval`; brain-mode scripts must follow the work order exactly.

---

## 7. Installation and registration

### 7.1 Commands produced by `mlca mcp install`
The helper prints the exact command or snippet for the chosen client. It runs a client CLI only with `--yes` and only if that CLI is on PATH. It never edits another tool's config file without `--yes`; with `--yes`, it backs the file up first.

| Client | Registration |
|---|---|
| Claude Code (user) | `claude mcp add --scope user mlca -- mlca mcp --mode brain` |
| Claude Code (project, shared through `.mcp.json`) | `claude mcp add --scope project mlca -- mlca mcp --mode brain --project .` |
| Codex | `codex mcp add mlca -- mlca mcp --mode brain` (stored in `~/.codex/config.toml`) |
| Hermes | snippet for `~/.hermes/config.yaml`: `mcp_servers: {mlca: {command: mlca, args: ["mcp", "--mode", "brain"]}}` |
| Cursor, generic clients | JSON snippet `{"mcpServers": {"mlca": {"command": "mlca", "args": ["mcp", "--mode", "brain"]}}}` and the file path the client documents |

OpenClaw implementation update (M6): its native registry is `mcp.servers`, registered through `openclaw mcp set mlca <server-json>`; it does not use the generic `mcpServers` entry. Hermes uses its locally verified `mcp add` CLI, with the equivalent YAML documented. User/project scope is supported by Claude and Cursor; Codex/Hermes/OpenClaw refuse project scope here. See `docs/DECISIONS.md`.

Before writing exact flags, check each client's current CLI help on this machine (`claude mcp add --help`, `codex mcp add --help`). Record the versions checked in `docs/mcp.md`.

### 7.2 Without a permanent install
- `uvx --from mlcagent==0.2.0b2 mlca mcp` and `npx mlcagent mcp` (the npm launcher forwards arguments).
- `docs/mcp.md` warns that the first run downloads packages and may exceed a client's server start timeout. Recommend `uv tool install mlcagent==0.2.0b2` first.

### 7.3 Agent skill
- `skills/mlca/SKILL.md`, at most 60 lines: what MLCA is, the two modes, the tool loop, the work-order contract, human-only decisions, and "do not try to bypass rules; failures are evidence".
- `mlca mcp install --with-skill` copies it to the client's skills folder where one exists (Claude Code `~/.claude/skills/`, the Hermes skills folder), after asking.
- It is optional: the server instructions alone must be enough.

---

## 8. Tests (`tests/mcp/`, offline; use the SDK's in-process or stdio client)

1. **Protocol:** the server starts, `tools/list` returns the 14 tools with valid schemas, and logs never reach stdout (stdout must stay clean MCP).
2. **Brain-mode full path:** using `tests/fixtures/` scripts submitted through `mlca_submit_script`, the synthetic classification project runs from `onboard` to `report`. Human approvals are done through the human API in the test (`resolve_approval` with the user principal). Then `replay --verify` passes, and the reports count agent and user decisions correctly.
3. **Driver-mode full path:** the same project, with the fake provider as MLCA's Worker, polling `mlca_step_status`.
4. **Bypass attempts through MCP, each refused and logged:**
   - calling human-only `Session` methods with an agent principal;
   - `mlca_submit_options` with an action outside the catalog, an unknown parameter, or an already-satisfied sub-goal;
   - `mlca_custom` naming the test set or an undeclared path (layer 1; zero model calls);
   - `mlca_submit_script` that:
     - reads the vault, the key directory or the original data after the split (level A: not visible);
     - imports `socket`;
     - calls `.fit` directly in a fit stage;
     - fits on validation rows;
     - writes outside `outputs/`;
   - submitting for a wrong or completed `step_id`;
   - `mlca_move` while a step is active;
   - `mlca_move` past a failing gate;
   - a stale `option_id`.
5. **Attempt limit:** three failing scripts lead to `StepFailed`; a fourth submission is refused.
6. **Privacy:**
   - with `allow_sample_rows: false`, no result contains a data row (scan results for values from the synthetic table);
   - each tool call writes exactly one egress line;
   - figures arrive as image content.
7. **Concurrency:** while an MCP step runs, a CLI `choose` gets "project busy", and vice versa.
8. **Install helper:**
   - `mlca mcp install --client claude` prints the expected command; `--client json` prints valid JSON;
   - nothing is executed without `--yes` (fake `claude`/`codex` executables on PATH record their arguments).
9. **Approvals:** request → CLI approve → the action is performed and `ApprovalResolved` is written; decline → nothing changes.

Before closing M6, revert two guards locally (the agent-principal check, and the layer-1 check in `mlca_custom`). Show that the tests fail, then restore them.

---

## 9. Phases

| Phase | Content | Done when |
|---|---|---|
| **M0** | Core prerequisite tests (section 0; tracked in `plan.md`) | listed tests pass |
| **M1** | Engine changes: principal, human-only refusals, approvals, resumable steps, per-attempt test exposure, mode config, Session additions (section 3) | unit + integration tests for each; CLI/TUI unchanged in behaviour; full suite green |
| **M2** | MCP server skeleton, read tools (`open`, `init`, `status`, `options`, `step_status`, `read`, `report`), server instructions, `mlca mcp`, `mlca mcp doctor` | tests 8.1, read-only parts of 8.6 |
| **M3** | Driver mode over MCP (`choose`, `custom`, `move`, `branch`, `request_approval`; background execution, polling) | tests 8.3, 8.7, 8.9 |
| **M4** | Brain mode (`submit_options`, `submit_script`, work orders, attempt flow, no model calls) | tests 8.2, 8.4, 8.5 |
| **M5** | Privacy and accounting for MCP (egress, usage by principal, image results, untrusted-data fields) | test 8.6; usage report shows principals |
| **M6** | Install helpers, `docs/mcp.md`, `skills/mlca/SKILL.md`, README section | test 8.8; docs reviewed; the guard-revert check (section 8) done |
| **M7** | Manual run by the author with real clients: Claude Code (brain), Codex (brain), Hermes (brain), the plain TUI (driver, with a configured provider) | checklist in `docs/mcp.md` filled in with versions, dates, what worked and what failed |

Commit locally per phase (`MCP M<n>: …`). Update `CHANGELOG.md`, `docs/IMPLEMENTATION_STATUS.md` and this file's *Status* section at the end of each phase.

---

## 10. Later (needs the author's go-ahead)
- Streamable HTTP transport (`mlca mcp --http 127.0.0.1:PORT`, bearer token, loopback only by default) for remote or shared machines.
- Claude Code plugin or MCP bundle (`.mcpb`) packaging, so the server and the skill install together.
- A2A (Agent2Agent) endpoint, if MLCA later runs as a networked lab service with its own models. MCP stays the local docking path.
- ACP (Agent Client Protocol) adapter for editors (reference: Hermes `acp_adapter/`).

---

## 11. Review checklist (used when the work is done)
1. In both modes, no MCP path can confirm a sub-goal, unlock the test set, approve a package, or write to the log outside `Session` (tests).
2. Brain mode makes zero model calls: the fake provider is unconfigured and the run still completes.
3. Every agent-written script passes through the same static checks, sandbox and fit rules as Worker scripts (same functions; no MCP-specific shortcuts).
4. Attribution is correct: every agent action carries `agent:<name>/<version>`, and reports split human from agent decisions.
5. Results are compact and privacy-filtered, and each one is logged in egress.
6. stdout carries only MCP messages.
7. Registration commands were checked against the installed client CLIs; nothing was registered without `--yes`.
8. The CLI and TUI behave as before; the full suite is green.

## 12. Review findings (2026-10-07, commit `4b6c2fb`) — to fix before M7

Reviewer check: full suite **81 passed, 1 skipped**, reproduced. A live stdio session (SDK client, brain mode) worked:
- 14 tools discovered;
- an agent approval request was approved through the human CLI;
- attribution `agent:<client>/<version>` recorded;
- the work order matches the Worker prompt.

Two privacy and trust gaps were found.

### R-MCP1. Raw data rows can reach the agent despite `allow_sample_rows: false` (confirmed)
**Reproduced:** in `eda`, a submitted script saved `df.head(8)` as the required `distributions.csv`. The step completed, and `mlca_read(kind="table")` returned the 8 raw rows verbatim. The 50×12 limit does not stop verbatim rows.

**Fix:**
1. When `allow_sample_rows` is false, give every table and fact value returned over MCP a **row-fingerprint guard**:
   - at registration and at split, store salted hashes of every data row (values rounded to 6 significant digits, column order normalised) in `.mlca/private/row_fingerprints`; the store is never readable by steps;
   - refuse a table read if any returned row, restricted to columns shared with the data, matches a fingerprint;
   - refuse fact values that equal a full data row.
2. At `collect` time, mark such outputs `contains_data_rows: true`, so they are never readable over MCP and are flagged in reports.
3. **Test:** the reproduction above is refused; a genuine `describe()` summary is still readable.
4. **Docs** (`docs/mcp.md`, README): say plainly that in brain mode the agent writes the code, so derived outputs (figures with individual points, small-group summaries) can still reveal data to the agent's model provider. The guard blocks verbatim rows only. For data that must not leave the machine, use driver mode with a local model.

### R-MCP2. The agent's own file and shell access bypasses MLCA's interface (documentation and setup)
**Problem:** Claude Code and Codex normally also have their own file and shell tools. Outside MCP they can:
- read `data.csv`, `.mlca/data/splits/*.parquet` and the test-set key in `~/.local/share/mlca/keys/`;
- run `mlca approvals approve`, `mlca unlock-test` or `mlca confirm` themselves.

MLCA's guarantees cover only what passes through MLCA. `docs/mcp.md` mentions the CLI and file modification, but not reading the data or the key.

**Fix:**
1. Add a "Trust boundary" section to `docs/mcp.md` and the README, stating exactly the above.
2. `mlca mcp install` prints a recommended client permission block, and writes it only with `--yes`, backing up the file first. For Claude Code, project `.claude/settings.json` `permissions.deny`:
   - `Read(./.mlca/**)` and `Edit(./.mlca/**)`;
   - reads of the registered data paths;
   - `Read(~/.local/share/mlca/**)`;
   - `Bash(mlca approvals:*)`, `Bash(mlca unlock-test:*)`, `Bash(mlca confirm:*)`, `Bash(mlca package:*)`.

   For Codex and others, print the equivalent guidance in prose, or the client's sandbox setting if it has one. Check the exact permission syntax against the installed client versions and record them.
3. Reports state the agent's file access as `unknown (outside MLCA)`, never as restricted.
4. **Test:** the install helper preview contains the deny block; nothing is written without `--yes`.

### Core gap found in the same run (fix tracked in `plan.md` → Status)
Supporting actions are effectively unreachable without a Navigator:
- the fallback offers only default and primary actions;
- once an event is done, only `next` is offered and `custom` is refused.

So `count_target`, `plot_missingness`, `plot_results` and the `audit_*` actions never appear in plain driver use or in an agent's option list.

### Follow-up review (2026-10-07, commit `6103b55`)
Reviewer reproduction: suite 96 passed, 1 skipped; live stdio, brain mode.
- **Supporting-action menu:** fixed. `data` offers `audit_schema, count_target, custom` before and `next, count_target, custom` after.
- **R-MCP2:** fixed. `mlca mcp install --client claude --scope project` previews a deny block covering:
  - `.mlca/**`, the key directory and the registered data file;
  - the `tables/`, `figures/`, `reports/` and `scripts/` views;
  - the four human commands, plus the shell entirely (`Bash`), with bypass mode disabled.

  Nothing is written without `--yes`. Flags match Claude Code 2.1.292.
- **R-MCP1:** partly fixed. A verbatim copy (`df.head(8)` under the original column names) is now flagged and refused. Two simple evasions still pass, and `mlca_read` returned the raw rows:
  - **renamed columns:** `df.head(8).rename(columns=str.upper)`;
  - **rounded values:** `df.head(8).round(4)`, in a custom step.

**R-MCP1b (implemented; final validation in Status):**
1. **Column-name-independent matching:** look up each cell's digest across all columns of a dataset (the `cells` table already supports this), not only same-named columns.
2. **Precision tolerance:** store cell digests at 6 and at 4 significant digits.
3. **Row rule:** flag a row when at least `min(3, n_columns)` of its cells match the same data row.
4. **Tests:** the reproductions above (renamed, rounded) are refused; a `describe()` summary, a class-count table and a metrics table still read normally.
5. **Docs** (README, `docs/mcp.md`): the guard catches accidental and simple copies, not a deliberate agent. The agent writes the code, so it can always encode data in outputs (noise, strings, figures). For confidential data, use driver mode with a local model; brain mode sends derived results to the agent's provider by design.

## 13. Aligning MCP with the guided TUI (P11), before M7 (2026-10-13)

P11 (`plan.md`) changed what an option *is*:
- the engine now appends human-decision cards (`engine/guidance.py: cards`);
- study fields can be deferred ("I'll decide later") and set only by a human (`api.py: resolve_study`, human-only);
- models can change between steps (`change_models`, human-only, `ModelChanged`);
- progress has phases, and records have a plain-language message map (`ui_text.py: record_message`).

The MCP server predates this. The reviewer checked the code at `757c936` and found these gaps for the M7 brain-mode run:

| # | Gap | Effect in brain mode |
|---|---|---|
| G1 | `mlca_options` returns human cards with ids like `opt:<rec>:human:confirm:brief_confirmed`. `mlca_choose` splits the token on every `:` and expects exactly 3 parts | Choosing a human card fails with **"Option is stale"**, which is wrong and confusing. Nothing tells the agent that the card is the human's |
| G2 | Deferred study fields: `resolve_study` is human-only, and `request_approval` supports only `confirm`, `unlock_test`, `package` | If the target was deferred, the agent **cannot ask** for it to be set. The study is stuck in `onboard` unless the user knows to open the TUI's Study details |
| G3 | The TUI refreshes only on in-process record callbacks (`session.subscribe`) | With Claude driving through `mlca mcp`, a TUI opened in a second terminal **does not update** when the MCP process writes records |
| G4 | `mlca_status` has no journey and no plain-language activity; `mlca_step_status` has no phase; one progress notification per call | The agent cannot tell the user, in their chat, where the study is or what just happened in the words the TUI uses |
| G5 | Server instructions and `skills/mlca/SKILL.md` describe only the pre-P11 loop | The agent does not know about human cards, deferred fields or the guided card style |
| G6 | The model status line assumes driver mode | In brain mode the TUI would show "not connected: press m" while Claude is the brain |

Driver mode over MCP is also affected by G1, G3, G4 and G5.

### MX1 · Human cards over MCP (G1)

**Implemented:** typed guided cards, bounded token parsing and human-decision refusals; focused offline tests pass.
- Parse option tokens as `opt:<record_id>:<rest>` (split at most twice), so human card ids survive intact.
- In `mlca_options`, every card carries `actor: "agent" | "human" | "engine"`. Human cards also carry `how`: the exact call that requests them, e.g. `{"tool": "mlca_request_approval", "kind": "confirm", "target": "brief_confirmed"}`, `{"kind": "unlock_test", "target": "test"}`, or `{"kind": "study_fields"}` (MX2).
- `mlca_choose` on a human card returns a clear refusal with that same `how` ("This decision is yours to request, not to make: call mlca_request_approval(…)"). It is logged as a `Refusal` with category `human_decision`. It never says "stale".
- The navigation card `next` and loop cards stay choosable by the agent, as today. Gates still apply.
- **Tests:** an MCP client sees `actor` and `how` on each human card; choosing one gets the specific refusal; the token parser accepts ids containing `:`.

### MX2 · Study fields as an approval request (G2)

**Implemented:** validated proposals, user-only resolution, CLI --edit and prefilled TUI form; focused offline tests pass.
- Add `study_fields` to `request_approval` kinds. The agent may attach **proposed** values with a reason: `{target, duration, event_column, unit, repeated_subjects, primary_data}`. They are validated against the inventory's columns, but nothing is applied.
- **Human side:**
  - `mlca approvals approve <id>` applies the proposed values through `resolve_study` as the user, after showing them;
  - `--edit` lets the human change them first;
  - the TUI approval dialog pre-fills the Study details form with the proposal.

  The record states both the proposer (agent) and the decider (user).
- `mlca_init` from an agent keeps working. If it leaves fields deferred, its result says so and names MX2's request as the next step.
- **Tests:** agent proposes → human approves → `StudyFieldsResolved` with actor `user`, proposer `agent:…`; a decline leaves the state unchanged; invalid column names are refused at request time.

### MX3 · A live TUI next to an MCP session (G3, G6)

**Implemented:** incremental external polling, brain-mode attribution and waiting-script confirmation approval; focused Textual tests pass.
- The TUI also polls the event log (about every 1 s, using the incremental `Store` read) and refreshes cards, sub-goals, facts, the journey and the status when another process wrote records.
- **While another principal holds an active step or the project lock:**
  - the cards are greyed out, with "Claude (agent:…) is working on step <id>: <phase>";
  - human cards and approvals stay usable (resolving an approval does not need the step lock, or it waits briefly and retries).
- **Model status in brain mode:** `● Brain mode · driven by agent:<client>/<version> · MLCA makes no model calls`, instead of "not connected". `m` still opens Models, for later driver use.
- **Tests:** Textual pilot with a second `Session` writing records from another thread or process → the TUI updates within 2 s; human-card approval works while the agent's step is waiting for a script.

### MX4 · Journey, messages and phases for the agent (G4)

**Implemented:** bounded branch projection, durable controlled phases, SDK progress callbacks and single-call accounting; brain/driver phase and privacy tests pass.
- **`mlca_status` adds:**
  - `journey`: the events with states `done | current | locked | ahead`, and the current branch's action trail (last 12 steps and human decisions, each with its actor);
  - `messages_data`: the last 10 plain-language lines from `record_message`, as untrusted data.

  The agent can paste these to the user.
- **`mlca_step_status` adds** `phase`:
  - brain mode: `awaiting_script | checking | running (attempt n/max) | collecting | checking_subgoals | completed | failed`;
  - driver mode: `writing` as well.

  Progress notifications are sent at each phase change, where the client supports them; polling stays the guaranteed path.
- **Privacy:** these fields pass through the same serializer, egress logging and row guard as other results. The messages carry no data rows.
- **Tests:** status contains journey and messages after a step; phases move in order in brain and driver modes; egress is logged once per call.

### MX5 · Instructions, skill and the guided card style (G5)

**Implemented:** 15-line instructions, guided default skill and source-aware VM walkthrough; focused offline tests pass. Installed source refresh follows this phase.
- **Server `INSTRUCTIONS`** (still at most 15 lines) add:
  - cards have an `actor`; human cards are requested, never chosen;
  - deferred study fields go through `request_approval(kind="study_fields")`;
  - read `journey` and `messages_data` to keep the user informed.
- **`skills/mlca/SKILL.md`** adds a **guided style** as the default: before each choice, show the user the current cards as a short numbered list (title, one line, actor), and ask which one, unless the user has said "choose yourself". Restate the journey in one line after each step. Autonomous style stays available.
- **`docs/m7-vm-brain-mode.md`:**
  - second terminal: open `mlca -p .` (the live TUI from MX3) to watch and approve, or use `mlca approvals`;
  - the Claude prompt updated to the guided style;
  - the deferred-target path covered.

### MX6 · Accounting and reports

**Implemented:** evidence-based proposal/decision/refusal counts, approval waits and script-source share; synthetic tests pass. Full-suite validation: 202 passed, 1 skipped.
- **Decisions by principal** also count: human cards requested by the agent; study-field proposals (proposed by agent, decided by user); and refusals with category `human_decision`.
- **`mlca metrics`** reports, for brain-mode runs: the number of agent-requested approvals, the human approval wait time (already timed in P10.2), and the share of steps whose script came from the agent.
- **Tests:** a synthetic brain-mode run → metrics show those counts.

**Order:** MX1 → MX2 → MX3 → MX4 → MX5 → MX6. Commit locally per sub-phase (`MX<n>: …`); keep the full suite green. Refresh the installed `mlca` after MX5, and publish **0.2.0b3** only when the author says so. No live model calls.

**Done when:** in a synthetic MCP brain-mode run, the agent:
- sees human cards with `how`, gets the specific refusal when choosing one, and proposes a deferred target via `study_fields`;
- is unblocked after the human approves in the CLI or TUI;
- reports journey and messages to the user.

Meanwhile, a TUI open in a second terminal updates live, shows "driven by agent", and resolves the approvals. All tests green.

## 14. Brain-mode benchmarking: the same tables and studies, driven by an external agent (2026-10-14)

### 14.1 Historical baseline (checked in code, `f430270`; superseded by WP3)

- **Brain and driver modes:** both work. There are 16 tools, including `mlca_questions` and `mlca_answer`. `mlca_options` runs the guided turn (P15), so MCP projects get the P14.4 data questions too. Human cards, study-field approvals (MX1/MX2), journey/messages (MX4) and accounting (MX6) are done.
- **Not done:**
  - **M7** (an author-run brain-mode study with a real client) has never been run.
  - **`mlca bench` refuses brain mode** (`evaluation/bench.py` l. 164). There is no headless way to run a task card through Claude Code, Codex or OpenCode.
  - **`mlca mcp install`** supports `claude`, `codex`, `hermes`, `openclaw`, `cursor`, `json`, but **not `opencode`**.
  - **`mlca usage import`** reads Claude and Codex session files only.
  - **Brain-mode token totals** come from client session files after the fact. There is no per-run capture.

### 14.2 Goal: one comparison across modes and models

| Arm | Who decides and writes code | Models | Token source |
|---|---|---|---|
| **driver** (`mlca bench`) | MLCA's own Navigator + Worker | the 6 chosen models via OpenRouter | MLCA request ledger |
| **brain / OpenCode** | OpenCode agent over MCP | **the same OpenRouter models** (like-for-like with driver) | OpenCode run output |
| **brain / Claude Code** | Claude Code over MCP | `anthropic/claude-haiku-5.5` (and the author's choice) | `claude -p --output-format json` usage |
| **brain / Codex** | Codex over MCP | `openai/gpt-6-luna` (and the author's choice) | `codex exec --json` usage |

The no-AI reference arm is not part of the comparison (author, 2026-10-14). The same task cards are used for the six bench tables and the bio-bench studies S1–S4. The same metrics are reported: completion, failures by category, recovery, interventions, Navigator fallbacks (driver), scope refusals, time split, tokens, cost.

### 14.3 Work items (MB1–MB6), in order

- **MB1 · `opencode` client.** Add `opencode` to `mcp/install.py`: a project-scope `opencode.json` with a local MCP server entry for `mlca mcp serve --mode brain`. Preview by default; write only with `--yes`. Verify the exact config keys with the installed `opencode` (`opencode --help`, its docs); do not guess.
- **MB2 · Isolated client sandbox per run.** Every brain-mode run gets a fresh config directory for the client (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`, OpenCode config path). It contains only the MLCA MCP server, and the client's own file-write and shell tools are disabled or restricted to the run folder:
  - Claude: `--allowedTools` limited to `mcp__mlca__*`;
  - Codex: read-only sandbox;
  - OpenCode: deny write/bash permissions.

  This closes R-MCP2 for measured runs. Record the exact flags in `bench.json`.
- **MB3 · `mlca bench run --mode brain --client <opencode|claude|codex> --model <id>`.** For each run:
  1. Create the project from the task card, as in driver mode.
  2. Write a fixed prompt file generated from the card: aim, data, template, the ordered custom instructions for bio-bench, and "use only the mlca tools".
  3. Launch the client headless with a wall-clock limit:
     - `opencode run`;
     - `claude -p --output-format json --mcp-config … --model …`;
     - `codex exec --json …`.

     Verify every flag against each tool's `--help`.
  4. A **policy approver** thread resolves human-only approvals (brief and validation confirmation, test unlock, packages) exactly as the card's `approval_policy` declares. It records principal `user:policy/<card sha>`; the agent never approves.
  5. Save the client's raw JSON output and transcript in the run folder.
  6. Run `mlca metrics`.

  The run is a failure if the client exits without completing the workflow; keep it.
- **MB4 · Usage capture.** Parse client-reported usage from the saved raw output (input, output, cached and reasoning tokens, cost if reported; unknown stays `null`). Store it as `external_agent` records with `cost_source: client`. Extend `mlca usage import` to OpenCode. MLCA's own requests (none in brain mode except the reference arm) stay separate.
- **MB5 · `bench summarize` across arms.** Group by arm × client × model × task. Put brain and driver numbers in one table with the same columns. Mark fields unavailable in an arm (e.g. Navigator fallbacks in brain mode) as `n/a`, never `0`.
- **MB6 · M7 smoke.** One brain-mode run per client on `heart_disease_cleveland_uci.csv`, offline-first with a scripted check, then live **only with the author's go-ahead**. It replaces the manual M7 checklist as the acceptance test.

### 14.4 Acceptance

- Offline tests:
  - `opencode` registration preview;
  - the prompt file built from a card;
  - the policy approver resolves only declared approvals;
  - usage parsing from recorded client outputs (fixtures);
  - mixed-arm summarize.
- A brain-mode project can never be approved by the agent principal (existing invariant; add a test through MB3).
- One authorised live smoke per client completes or fails with a recorded category; its tokens appear in `mlca usage`.

## Status

**14 October WP3/WP6:** MB1–MB5 implemented locally in bbc72fd: OpenCode registration,
private headless configs, task-card brain bench/bio-bench, separately attributed policy approvals,
client-reported usage and cross-arm summaries. All three installed headless flag sets were
checked against --help. Offline acceptance: 25 regressions and 12 final focused tests passed.
No MB6/live model calls. The remote is HawkFranklin-Research/mlcagent; local master began at
f430270 and now includes WP1–WP4. No measurement freeze exists. WP7 now finished: full suite 296 passed, 1 skipped;
seven zero-call reference attempts and audited exports, with failure/not-achieved outcomes retained.
No live brain-client validation (MB6); see docs/IMPLEMENTATION_STATUS.md.
Historical status entries below describe their dated commits, not current deficiencies.


- **2026-10-13 MX review (`64c7a52`):** suite 202 passed, 1 skipped, reproduced. A live stdio brain-mode session verified MX1–MX4: human cards with `actor`/`how`; the specific refusal; a `study_fields` proposal approved in the CLI, recorded with its proposer; an invalid column refused at request time; journey, messages and phases. MX3 polling and the MX5 guided style are present.

  Small wording fixes, implemented (2026-10-13):
  1. `messages_data` shows "→ Continue to onboard" after study fields change (`EventEntered` via `study_fields_updated`). It should say "↻ Onboard re-checked after your study details".
  2. "✓ Approval approved" should be "✓ You approved: <kind>".
  3. Invalid `study_fields` proposals now use `invalid_request`; integrity exceptions retain their category.

  Approval resolution records now carry `kind`; historical records remain readable without rewriting the log. Regression tests cover re-check messages, approved/declined wording, invalid columns and malformed proposals.

- **2026-10-13 MX implementation:** MX1–MX6 implemented in ordered local commits. Full offline suite: **202 passed, 1 skipped in 719.16 s** (PowerShell unavailable). Ruff lint/format pass. Installed source refreshed after MX5; final refresh includes MX6. No live model calls, computer controls, remote pushes or beta 3 publication. Public beta 2 is unchanged; local development source still reports 0.2.0b2. Master and browser plans remain untouched.

## Beta 2 published and beta 1 yanked — 2026-10-13

Published [mlcagent 0.2.0b2](https://pypi.org/project/mlcagent/0.2.0b2/) using the authorized upload token; both public artifact hashes match. Fresh isolated HOME/XDG PyPI install, version, doctor and 14-tool MCP verification pass. Beta 1 is yanked (both files), verified in release management and public PyPI JSON. Local tag v0.2.0b2 records release source bdc2f376ef2b9b2848d5f5ed5b272ee9aad2a311; global mlca was refreshed to 0.2.0b2. No GitHub/npm push or publication occurred. Master and uncommitted browser plans remain untouched.

Final suite: 193 passed, 1 skipped in 647.09 s; lint/format, metadata, wrappers, Twine, wheel resources and isolated synthetic init/permission-preview pass. Real OAuth/model/data validation and OpenAI registration remain pending. The token was read only by the publish command and never displayed, copied or committed.


**2026-10-13 beta 2:** Full offline suite: **193 passed, 1 skipped in 647.09 s** (PowerShell unavailable). Ruff lint/format, release metadata and wrapper checks pass. Rebuilt wheel/sdist pass Twine and the 206-entry wheel check. Isolated HOME/XDG install, version/doctor, synthetic initialization and 14-tool MCP discovery pass; Claude registration/skill preview writes no configuration. No live models, real OAuth authorization or original-data study was run. Native P11 changes preserve all 14 MCP tools. Upload/public verification follows; b1 yank is authorized after b2 verification.

### Beta publication attempt — 2026-10-07

- D1 is resolved as CC-BY-NC-ND-4.0; D3 was author-approved as `mlca`. Release source is local commit `ac4bcc8`; incoming VM docs were committed separately as `45344a5`.
- Release gates pass: **106 passed, 1 skipped** (PowerShell unavailable), Ruff lint/format, approved-name/version guard, synchronized wrappers, wheel/sdist build, Twine checks and all 179 wheel resources.
- The built wheel passed the isolated HOME/XDG walkthrough: version, doctor, synthetic study init, Claude project/skill preview with no configuration writes, working bubblewrap namespaces and official stdio discovery of all 14 tools.
- **Publication blocked:** the single authorized `uv publish` attempt received HTTP 400 on the first artifact: PyPI rejected `mlca` as too similar to an existing project. No file was accepted; the public project JSON endpoint still returned 404 afterwards. This was a name-validation response, not an invalid-token response.
- There is **no published PyPI URL**. Registry acceptance requires a replacement author-chosen name or resolution with PyPI. A JSON 404 does not establish that a name can be registered. `mlca-agent` also returned 404, but its acceptance is unverified.
- Fresh installation from PyPI and the release tag are deferred until publication succeeds. No GitHub push, npm publication or remote creation occurred. No real client/model/original-data run was performed; M7 remains pending.


- **2026-10-07 R-MCP1b:** implemented in `privacy/rows.py`: column-name-independent
  distinct-cell matching at six/four significant digits, plus safe version-1 migration.
  Full-row facts also ignore column names/order. CSV/Parquet collection and read-time guards
  reuse it. Tests: `tests/unit/test_row_fingerprints.py`, `tests/mcp/test_row_privacy.py`;
  focused run **14 passed in 25.35 s**, including both reproductions and readable summaries.
  README/MCP/security docs and generated trust reports describe simple-copy detection and its
  deliberate-encoding limits. **Full suite: 101 passed, 1 skipped in 421.09 s**; Ruff,
  wheel/resource checks and installed-wheel 14-tool discovery pass. M7 remains author-run.
- **2026-10-07 R-MCP1/R-MCP2:** implemented. Private salted row/cell fingerprints cover
  registration and splits; copied tables are flagged at collection and refused at MCP read,
  including legacy artifacts. Full-row facts are refused, and report reads remove run diagnostics.
  Claude install previews recommend denies; `--yes` backs up and merges project permissions.
  Other clients receive prose guidance. Reports mark external file access unknown. Code:
  `privacy/rows.py`, `runner/artefacts.py`, `engine/turn.py`, `mcp/server.py`,
  `mcp/permissions.py`, `mcp/install.py` and `report/`. Regressions:
  `tests/unit/test_row_fingerprints.py`, `tests/mcp/test_row_privacy.py`, `tests/mcp/test_install.py`.
  Final validation is recorded in `docs/IMPLEMENTATION_STATUS.md`.
- **Prior review validation:** full offline suite **96 passed, 1 skipped (396.58 s)**;
  Ruff, skill and wheel checks pass. Installed-wheel stdio discovers all 14 tools. The skip
  is unavailable PowerShell analysis. No live providers or actual client registrations.
- **Supporting actions:** author approved on 2026-10-07, implemented in `engine/options.py` and
  `api.py`: unrun supporting actions follow primaries; completed events offer `next` first,
  unrun supporting actions and scoped custom. Primary proposals after completion are refused;
  supplementary steps preserve checks/generation. Tests: `tests/unit/test_options.py` and
  `tests/mcp/test_supporting.py` and `tests/integration/test_driver_supporting.py`.
  This supersedes the earlier next-only decision below.
- **2026-10-07 follow-up baseline:** menu fix and R-MCP2 verified; R-MCP1 was partial,
  leading to R-MCP1b above. Reviewer baseline: 96 passed, 1 skipped.
- **2026-10-07 review:** M0–M6 verified (81 passed, 1 skipped; live stdio session OK). Fix R-MCP1 and R-MCP2 (section 12) before M7.
- **2026-10-07:** M0–M6 implemented and tested; M7 is pending manual author runs, recorded in `docs/mcp.md`.
- **2026-10-06 baseline:** plan written; implementation had not started.

## 2026-10-07 — MCP M0

Core prerequisite regressions added: gate refusal, untrusted model completion claims, Navigator repair/fallback, zero-call deterministic scope rejection, immutable step modes, invalid fact rejection, Worker static-failure repair, budget refusal, rate-limit retry and a credential canary scan. Targeted offline run: 7 passed. Live providers remain deferred. Incoming author/reviewer edits were preserved in a separate local checkpoint.

## 2026-10-07 — MCP M1

Caller principals are persisted for decisions and branch operations. Human-only confirmations, test unlocks and package approvals refuse agents in Session. Approval requests can be resolved through CLI/TUI; unlock still requires the exact phrase, and stale event/branch requests refuse approval. Brain steps persist ScriptRequested work orders and resume after reopen; both sources share run_attempt. Test decryption now lasts only around each execution. Active steps block movement/branching and package approval. Model calls are disabled at Client in brain mode. Background operations hold the same action lock; polling is available through step_status. Reports split decisions and script attempts by principal/source.

Validation: full offline suite 63 passed, 1 skipped (PowerShell unavailable), 242.09 s; focused engine/scientific checks after final guard edits: 4 passed. Unit/TUI subset: 28 passed. No live models called.

Deviation: an operation that has not reached StepStarted within one second returns a temporary operation ID; step_status resolves it to its eventual persisted step ID. This keeps provider option generation from blocking MCP. Operation IDs are connection-local; actual steps/work orders are persisted. Plain CLI/TUI remain blocking driver clients.

## 2026-10-07 — MCP M2

Official SDK mcp 2.3.0 is a core dependency (`mcp>=2.3,<3`); it exposes MCPServer, the successor of FastMCP. The real stdio doctor negotiated MCP 2026-07-28. In-process tests cover both modern auto negotiation and the legacy initialization path. Seven initial read/setup tools, compact views, indexed evidence reads, Context-derived agent identity, server instructions and `mlca mcp`/doctor are implemented. Protocol/read tests: 2 passed. CLI startup errors now use stderr so they cannot corrupt the protocol stream.

Resource deviation: the SDK disallows Context injection in static resources. Views therefore use `mlca://view/{kind}` (status/facts), ensuring per-request attribution and accounting. Optional tasks remain deferred because polling is universal and the SDK does not implement that extension. SDK references: https://github.com/modelcontextprotocol/python-sdk/releases and https://py.sdk.modelcontextprotocol.io/ .

## 2026-10-07 — MCP M3

Driver-mode choices/custom work run in background threads, movement/branches use Session, and human requests route to CLI approvals. MCP option IDs include the OptionsProposed record ID, rejecting consumed or stale menus. Polling reports running until execution, checks, facts and views finish and the project lock is released. Completed events refuse direct custom actions as well as offering only transitions.

Validation: MCP protocol plus full synthetic driver path and concurrent locking in both directions: 4 passed (30.70 s). Agent approvals were resolved by the human CLI; attribution/integrity checked. Persisted external-step regression: 2 passed. No real providers called.

## 2026-10-07 — MCP M4

All 14 stable tools are registered. Brain mode validates submitted options and scripts through the shared engine and returns persisted work orders/repair diagnostics. Option IDs are evidence-bound. Work-order hashes are computed after credential redaction. Runtime fact candidates with missing outputs now explicitly produce FactRejected instead of being silently dropped.

Validation: brain full synthetic classification path (including human approvals, image read and fresh-script replay) completes with Client.complete disabled and roles/providers removed. Brain bypass/attempt-limit tests and submitted execution guard tests at both available isolation levels: 4 passed, 87.42 s. Guards exercise forbidden imports/direct fit, validation fit, outside writes, and dynamically constructed paths to the real vault/key/original data. Protocol and persisted engine subset: 4 passed. No real models called. Background submission validates the persisted step state rather than its transient polling status.

## 2026-10-07 — MCP M5

Each dispatched tool/resource result creates one recoverable usage/egress envelope: principal, tool, duration, application-body bytes/hash and content categories. No result content is stored in that ledger. Calls before a project opens use an external per-server user-data ledger. Protocol/schema rejections outside a dispatched tool are handled by the SDK and are not project operations. SDK-added transport identity metadata is outside the application digest.

MCP usage has cost_source external: external agent tokens/cost are unavailable, not a claim that its inference is free. Model requests and external tool calls are counted separately, and tool time is excluded from LLM latency. Read views suppress raw inventory rows and stdout/stderr, and allow only indexed/hash-checked scripts, PNG figures, reports and bounded summary tables. Untrusted content stays under data fields and summaries are fixed text. Figure reads return ImageContent; evidence resources use query refs. Unknown exceptions expose their type only; application refusals are logged when the action lock is free, otherwise in the request ledger.

Validation: complete MCP suite 10 passed (122.70 s); focused ledger/privacy tests 2 passed after final changes. Tests verify one envelope per dispatched call, exact body hash/bytes, no synthetic-row canaries or fake key in results/ledgers, and external calls not counted as unknown model costs. These checks cannot prove arbitrary generated artifacts never encode individual data; summary content/figures still require scientific inspection. Same-user filesystem/CLI access is not authenticated by MCP clientInfo; human-only enforcement is an API boundary, not an OS identity guarantee.

## 2026-10-07 — MCP M6

Client registration previews/helpers, a bundled 38-line agent skill, MCP setup/tool/approval docs,
and updated README/plans are implemented. Helpers require --yes, back up existing files, run
CLI argv without a shell and preserve Cursor settings. Registration flags were checked for
installed Claude Code 2.1.291, Codex 0.160.1 and Hermes v0.21.5+8071; absent OpenClaw/Cursor
use official formats with native validation explicitly pending. MCP checkout now returns only
its compact overview, briefs scrub known credential values before persistence, unexpected
submitted-step failures freeze evidence, and bounded Parquet reads inspect row metadata first.

Guard sensitivity: disabling the human-principal check made
`test_agent_refusals_and_human_approvals` fail (1 failed, 0.74 s); disabling deterministic
scope rejection made `test_mcp_layer_one_rejects_before_step` fail (1 failed, 1.27 s).
Both guards were restored byte-for-byte before the final suite. Focused helper/init/guard tests
passed (7 passed, 2.37 s); bounded CSV/Parquet and init checks passed (2 passed, 3.45 s).
Skill validation, Ruff lint/format, wheel resource validation and a clean installed-wheel stdio
doctor pass. The doctor negotiated 2026-07-28 and found all 14 tools. Native client registration
was not performed; the wheel doctor used a client-free PATH and isolated MLCA config/data.

M7 remains an author-run checklist in docs/mcp.md: Claude/Codex/Hermes brain and live-provider
TUI driver. Anemia data, native macOS/Windows and live provider validation remain pending.

Final M6 validation: `uv run pytest -q` — **81 passed, 1 skipped in 360.22 s**.
The skip is PowerShell validation because pwsh/PSScriptAnalyzer are absent. The focused
helper/init/guard subset was rerun after the final Claude config-target correction (7 passed).
Ruff check and format check pass (140 files); Git whitespace check passes. Both templates
remain the author's incoming concise v0.2.0 content. No model calls, original-data runs,
client registrations, remote operations or publication were performed.

## 2026-10-07 — Author-approved replacement distribution

The author chose `mlcagent` for the 0.2.0b1 PyPI beta, superseding `mlca` and the suggested legacy name. The executable, imports, MCP tools and state folders remain `mlca`. Wrapper identities, installers and metadata now use `mlcagent`. The earlier rejected upload is retained above as historical evidence. One beta PyPI upload is authorized after release validation; GitHub pushes, new remotes and npm publication are not authorized.

## 2026-10-07 — P10 and mlcagent beta release gates

P10.1–P10.7 are implemented. Final full offline suite: **137 passed, 1 skipped in 603.43 s** (PowerShell unavailable); supporting-action/failure targeted subset: 20 passed. Ruff lint/format, approved-name/version guard, wrapper synchronization, build/Twine and 186-entry wheel resource checks pass. The final isolated HOME/XDG wheel walkthrough passes install/version/doctor, synthetic init, Claude project/skill permission preview without writes, bubblewrap namespace probe and stdio discovery of all 14 tools. No live models, original anemia data or native client/OS validation were performed. The authorized PyPI upload as `mlcagent` 0.2.0b1 follows; npm/GitHub operations remain unauthorized.

## 2026-10-07 — Published-beta verification

[PyPI release](https://pypi.org/project/mlcagent/0.2.0b1/). Fresh PyPI verification used an empty temporary HOME/XDG and uv cache: `uv tool install mlcagent==0.2.0b1`, `mlca --version` (0.2.0b1), `mlca doctor --json` (level A capability; execution must confirm isolation), and `mlca mcp doctor` (14 tools) all passed. Published wheel/sdist SHA256 hashes match the scanned release artifacts. Local tag `v0.2.0b1` points to release source `16bcc72`; no push. P10 is complete, while M7, real providers/data, and native macOS/Windows remain pending. The beta description contains an overlooked historical README Status paragraph; it is corrected in source for the next release, with no second upload. Token rotation to a project-scoped token and removal of the account-wide file remain an author account step; the file was read only by the publish command.
