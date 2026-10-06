# MLCA MCP server: implementation plan

Plan for a coding agent. It adds an **MCP server** to MLCA v2, so that general agents (Claude Code, Codex, Hermes, OpenClaw, Cursor, and any other MCP client) can drive an MLCA project. The engine's rules stay in force whoever is driving.

Written 2026-10-06. Companion to `plan.md`, which covers the core harness; read `plan.md` sections 0, 2 and 3 first. Every rule in `plan.md` section 0 applies here too: new code, offline tests, no hard-coded models, local commits only, nothing published. Record each decision in `docs/DECISIONS.md` and each deviation from this plan, with its reason.

---

## 0. Prerequisite (core work, tracked in `plan.md`)

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
| OpenClaw, Cursor, others | JSON snippet `{"mcpServers": {"mlca": {"command": "mlca", "args": ["mcp", "--mode", "brain"]}}}` and the file path the client documents |

Before writing exact flags, check each client's current CLI help on this machine (`claude mcp add --help`, `codex mcp add --help`). Record the versions checked in `docs/mcp.md`.

### 7.2 Without a permanent install
- `uvx mlca mcp` and `npx mlca mcp` (the npm launcher forwards arguments).
- `docs/mcp.md` warns that the first run downloads packages and may exceed a client's server start timeout. Recommend `uv tool install mlca` first.

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

## Status

- **2026-10-06:** plan written. Nothing implemented. Starts after the core prerequisites (section 0).
