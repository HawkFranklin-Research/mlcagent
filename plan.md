# MLCA v2: implementation plan

Plan for a coding agent. It specifies a new harness, **MLCA v2** (ML Copilot Agent, revised), to be built in this repository: `/home/prime/Documents/github/mlca-paper-codebases/mlca-revized/`.

Written 2026-10-06. When the code is done, it will be reviewed against section 13 (evaluation checklist). Read the whole file before writing code. Where this plan and the code you find disagree, stop and record the conflict in `docs/DECISIONS.md`. Do not guess.

---

## Current status — 2026-10-07

### Beta publication attempt — 2026-10-07

- D1 is resolved as CC-BY-NC-ND-4.0; D3 was author-approved as `mlca`. Release source is local commit `ac4bcc8`; incoming VM docs were committed separately as `45344a5`.
- Release gates pass: **106 passed, 1 skipped** (PowerShell unavailable), Ruff lint/format, approved-name/version guard, synchronized wrappers, wheel/sdist build, Twine checks and all 179 wheel resources.
- The built wheel passed the isolated HOME/XDG walkthrough: version, doctor, synthetic study init, Claude project/skill preview with no configuration writes, working bubblewrap namespaces and official stdio discovery of all 14 tools.
- **Publication blocked:** the single authorized `uv publish` attempt received HTTP 400 on the first artifact: PyPI rejected `mlca` as too similar to an existing project. No file was accepted; the public project JSON endpoint still returned 404 afterwards. This was a name-validation response, not an invalid-token response.
- There is **no published PyPI URL**. Registry acceptance requires a replacement author-chosen name or resolution with PyPI. A JSON 404 does not establish that a name can be registered. `mlca-agent` also returned 404, but its acceptance is unverified.
- Fresh installation from PyPI and the release tag are deferred until publication succeeds. No GitHub push, npm publication or remote creation occurred. No real client/model/original-data run was performed; M7 remains pending.


MCP M0–M6 is implemented; see [plan_mcp.md](plan_mcp.md) and [docs/mcp.md](docs/mcp.md).
The six missing engine-rule regressions, Worker repair, budget stop, rate-limit retry and
credential canary tests are now permanent offline tests. Brain/driver synthetic MCP runs,
submitted-code bypass checks, approvals, concurrency, attribution, privacy and registration
helpers are covered. Final validation totals are in [implementation status](docs/IMPLEMENTATION_STATUS.md).
Review fixes R-MCP1/R-MCP2 are implemented: salted row guards, copied-row artifact flags,
full-row fact refusals, client permission previews/backup/merge, and explicit unknown external
file access in reports. Tests cover copied versus aggregate tables, projection/rounding, legacy
views and private-store access. The author approved supporting actions and scoped custom
instructions after completion on 2026-10-07; implemented with `next` first, preserving completed
checks and generations. Details: `plan_mcp.md` section 12/Status.
R-MCP1b now extends simple-copy detection across column names at six/four significant digits,
using distinct-cell matches in the same row and atomic legacy-index upgrades. Renamed/rounded
copy and summary regressions pass (14 focused tests). Full current validation is in
`docs/IMPLEMENTATION_STATUS.md`; the prior review baseline was 96 passed, 1 skipped.
Docs explicitly distinguish the heuristic from confidentiality: brain-mode code can encode data
in outputs; confidential work needs local standalone driver models without remote recipients.
Final R-MCP1b validation: **101 passed, 1 skipped in 421.09 s**; Ruff, wheel/resource checks
and installed-wheel discovery of all 14 tools pass. No actual clients were registered.
M7 is explicitly an author-run client/provider checklist, pending. Original anemia data,
live providers, full survival scientific validation and native macOS/Windows remain pending.

## Baseline review (2026-10-06 at commit `61cb041`)

The following baseline results are historical; the current MCP status above supersedes its test gaps.

Legend: **✅ done** (code at the named location + test) · **🟡 done, untested or partial** · **⬜ not started** · **🔁 redesigned** (the code differs from the original spec; see R-list below).

**Overall:** P0–P8 implemented. P9 partially done: distribution only, brought forward at the author's request.
- **Tests:** `uv run pytest -q` gives **54 passed, 1 skipped** (PowerShell analyser unavailable). Confirmed by the reviewer in a clone.
- **Offline cache:** the tests run uv offline (`UV_OFFLINE=1`). On a fresh machine, run `uv run python scripts/prime_test_cache.py` once first; CI does this automatically.
- **Reviewer's manual run:** a synthetic project from `onboard` to `report` through the CLI, under sandbox level A. It covered the test lock, `replay --verify`, reports, branching and tamper detection.

History:
- P0–P8: commits `8a8a3c9` … `f56c9ef`.
- Startup fixes: `46fbb75`.
- Logo/banner: `6dc9309`.
- Functional fixes F3–F7: `bc6b254` … `d13bbcb`.
- Test suite: `1820066`.
- Distribution A–E: `b371aa5` … `61cb041`.

Work orders: `docs/prompts/01_functional_fixes.prompt.md`, `docs/prompts/02_distribution.prompt.md`. **MCP docking is implemented through M6 in [`plan_mcp.md`](plan_mcp.md)**; its prerequisite tests are complete. Running log: `docs/IMPLEMENTATION_STATUS.md`, `CHANGELOG.md`, `docs/DECISIONS.md`.

**Still open:**
- **Invariant test gaps closed in MCP M0:** `tests/integration/test_invariants.py` now covers I3/I4/I5/I6/I8/I9.
- **No real model calls yet:** Navigator options, fact extraction, Inspector, OpenAI/OpenRouter providers.
- **The §11 golden run on the real anemia data is not done;** the synthetic fixtures in `tests/fixtures/` stand in for it.
- **Template content v0.2.0** (D2): short goals, sub-goals and Do/Save/Record action prompts were written for both templates, plus an output contract in the Worker prompt (`docs/templates.md` → *Writing content*). The author should review the concrete defaults (split fractions, model families, primary metrics).
- **Native macOS/Windows not validated**; only level-B unit tests and CI definitions exist.
- **Supporting actions reachability fixed** (found and author-approved 2026-10-07):
  - `engine/options.py: fallback` offers only default and primary actions;
  - a completed event offers only `next`, and `api.py: custom` refuses custom instructions there.

  Those findings describe the prior behavior. The author approved and the code now implements:
  - append not-yet-run supporting actions after the primaries in `fallback`;
  - in a completed event, offer `next` first, then the supporting actions not yet run, plus `custom`, until the user moves on;
  - adding these steps does not reopen the event's sub-goals;
  - **tests:** `tests/unit/test_options.py`, `tests/mcp/test_supporting.py`: `count_target`
    reachable before/after `audit_schema`, scoped custom execution preserves completed checks,
    primary proposals remain refused, and out-of-scope custom instructions still fail.
- **P10 evaluation instrumentation** (planned 2026-10-07; run snapshot, decision timing, failure categories, `mlca metrics`, client-usage import, `mlca bench`): do before the author's VM test (section 8, P10).
- **P9 remainder:** general frontend RPC, Ink/Electron clients (the stdio MCP server is implemented), Illustrator, ChatGPT-account login, opencode free models.

### Redesigns and additions relative to the original spec (R-list)

| # | Area | Original spec | What was built (location) | Why |
|---|---|---|---|---|
| R1 | Event log | hash chain only | plus a `.mlca/log/head.json` checkpoint (detects last-line edits and truncation), and an incremental cached reader; full verification on `Session.open` and `mlca log --verify` (`log/store.py: Store._read`, `Store._incremental`) | integrity of the last line; read cost (F6) |
| R2 | Record types | §6.1 list | added `TurnStarted`/`TurnEnded`, `SplitFrozen`, `TestRead`, `ObservationRecorded`, `EnvironmentRecorded` (`log/schema.py`) | turn grouping, split and test-read evidence, Inspector notes, environment changes |
| R3 | Sessions | `SessionStarted` on every open | written lazily before the first mutating record; read-only commands write nothing (`api.py: Session._start_session`) | log noise (F6) |
| R4 | Actions | all model-written | `builtin: inventory \| split \| report` actions run engine code (`templates/model.py: ActionSpec.builtin`, `runner/run_step.py: _builtin`) | the split and reports must not be generated code |
| R5 | Templates | single-action `output_exists`; no action roles | `output_exists.any_of`, and `role: primary \| supporting` on actions, enforced by the loader (`engine/checks.py: evaluate`, `templates/model.py`, `templates/loader.py`) | alternative actions could never complete an event (F3) |
| R6 | Brief | verbatim answers only | `BriefRecorded.columns` with resolved column names, and `ProjectState.columns`; verbatim answers kept (`project/init.py`, `cli/main.py: pick_column`, `log/replay.py`) | the split read the target from free text (F5) |
| R7 | Test exposure | re-unlock allowed and logged | one-way: after any `TestUnlocked`, the fitting events (`split`, `preprocess`, `features`, `model`), validation loops and package approvals are refused project-wide (`api.py: _ever_unlocked`, `engine/turn.py: execute`, `api.py: package`) | stricter guard against tuning on the test set |
| R8 | Unlock | confirmation phrase | the fixed phrase `UNLOCK TEST` plus a required reason (`api.py: unlock_test`); per-split key `keys/<project_id>_<split_id>.key`; plaintext only in a temp file during `reads_test` steps (`sandbox/vault.py: seal`, `exposed`) | explicit and auditable |
| R9 | Sandbox level | B used automatically when bwrap is missing | B only with `sandbox.allow_level_b: true`, otherwise refuse; per-OS explanations (`sandbox/level.py: detect`, `explanation`); portable paths (`runner/process.py`) | honest isolation on macOS and Windows |
| R10 | Fit rules | `fit_record` + check | fit stages must fit only via `fit_record` and contain at least one; other events may not fit at all; `fit_record` requires the exact frozen training index and reports row counts on mismatch (`runner/static_checks.py`, `runner/run_step.py: _worker`, `mlca_runtime/__init__.py: fit_record`). The author keeps this strict | leakage control (I11) |
| R11 | Worker repair | truncated traceback | with `allow_sample_rows: false`, only the exception type and script line are sent (`runner/run_step.py: _worker`) | tracebacks can contain data values |
| R12 | Options | engine adds `next` when done | fallback offers primaries then unrun supporting actions; completed menus offer `next` first, unrun supporting actions and scoped custom; primary alternatives require a branch before completion (`engine/options.py`, `api.py`) | F4 and author-approved supporting-action reachability (2026-10-07), superseding the earlier next-only rule |
| R13 | Project integrity | — | template snapshot `.mlca/template` (sha-checked on open); runtime snapshot `.mlca/runtime/mlca_runtime` and env-lock hash checked before each step (`api.py: Session.__init__`, `runner/run_step.py: run_step`) | a study cannot silently change underneath |
| R14 | CLI | §7.8 list | plus `-p/--project`, `mlca templates list\|validate`, `mlca package`, `mlca web` (`cli/main.py`) | usability; browser view of the TUI |
| R15 | TUI | Textual app | compact logo banner and brand bar (`tui/banner.py`, `assets/logo.txt`, `assets/logo.png`, `scripts/make_logo.py`); key bindings moved per screen (`tui/screens/welcome.py`, `main.py`); helpers renamed to `_can_act`, `run_session_action` so they don't override Textual's own methods | author's logo (D5); startup crashes |
| R16 | Distribution | P9, later | brought forward and prepared, not published: wheel/sdist, `installers/install.sh` and `install.ps1`, npm launcher `packaging/npm/`, Homebrew `packaging/homebrew/`, CI and release workflows `.github/workflows/`, `docs/releasing.md`, `docs/install.md` | author request |

---

## 0. Rules for the coding agent

1. **New system, new code.** MLCA v2 is written from scratch in this repository. Other repositories are **references**: read them, reimplement the pattern. Copy a file only where section 9 says *copy*, and then add its attribution to `THIRD_PARTY_NOTICES.md`.
2. **Never modify** the legacy repository, the legacy experiments folder or the reference harnesses (section 1). They are read-only.
3. **The engine enforces rules; prompts do not.** Every rule in section 3 is implemented in code and covered by a test. A prompt may *explain* a rule to a model. A prompt is never the mechanism.
4. **Tests run offline.** Every test passes without network access or API keys, using the `fake` provider (section 7.6). Tests that use real models are marked `@pytest.mark.live` and skipped by default.
5. **No model names hard-coded in code.** Models come from configuration (section 7.6). Examples in docs may name models.
6. **Git:** `git init` in phase P0. Commit locally at the end of each phase with a message `P<n>: <summary>`. **Do not add a remote, push, or publish to PyPI or npm** without the author's explicit go-ahead.
7. **Secrets:** read API keys only from environment variables or the user config file (section 7.6). Never write a key into the repository, the event log, a project folder, a log line or a test fixture. Do not open files named `*keys*` anywhere on this machine.
8. **Vocabulary:** use the terms in section 2 exactly, in code, docs, UI text and commit messages.
9. Keep `docs/DECISIONS.md` (dated, one entry per non-obvious choice) and `CHANGELOG.md` (per phase) up to date.

---

## 1. Locations

| Path | Role | Access |
|---|---|---|
| `/home/prime/Documents/github/mlca-paper-codebases/mlca-revized/` | **this repository** (MLCA v2) | read/write |
| `/home/prime/Documents/github/mlca-paper-codebases/ml-copilot-agent/` | MLCA v1 (legacy, LlamaIndex event workflow, last commit 2025-05-04; branches `master`, `may4`, `v1.5`, `v-managers`, `gui`, `temp`) | read-only reference |
| `/home/prime/Documents/github/mlca-paper-codebases/mlca_experiments/` | legacy experiment data and outputs behind the submitted paper (not a git repo) | read-only; test data only (section 11) |
| `/home/prime/Documents/g3/support-git/hermes-agent/` | reference harness (Python core, Ink TUI, Electron desktop), MIT, commit `1e86b5240d` | read-only reference |
| `/home/prime/Documents/g3/support-git/opencode/` | reference harness (TypeScript), MIT, commit `631f67a9f3` | read-only reference |
| `/home/prime/Documents/g3/support-git/deepseek-harness/` | reference harness (TypeScript, plugin architecture), MIT, commit `5badb15009` | read-only reference |
| `/home/prime/Documents/github/derm-paper-codebases/pelliscope-train/` | reference for a well-structured ML project (numbered scripts, configs, run ledger, study lock) | read-only reference |
| `/home/prime/Documents/github/v-papers/ml_copilot_paper/` | the paper repository | **do not touch** |

Machine (checked 2026-10-06): Linux, Python 3.13 (`/home/prime/miniconda3/bin/python3`), `uv` at `~/.local/bin/uv`, `bwrap` (bubblewrap) at `/usr/bin/bwrap`, Node 22, npm. No Docker.

---

## 2. Vocabulary (use exactly these terms)

| Term | Meaning |
|---|---|
| **project** | a folder the user opens with MLCA; all state lives in `<project>/.mlca/` |
| **brief** | the user's short description of the data and the aim, recorded at project creation |
| **data inventory** | automatic read-only scan of registered data files (shape, columns, types, sizes, hashes) |
| **workflow template** | a declarative description of one kind of ML study (e.g. `tabular_classification`): its events, actions and checks |
| **event graph** | the events of a template and the allowed transitions between them |
| **event** | one stage of the workflow (e.g. `data`, `eda`, `split`). It has a goal, sub-goals, entry gate, allowed actions and a custom-instruction scope |
| **sub-goal** | a checkable condition inside an event, verified by a **check** (deterministic code), never by a model |
| **gate** | the condition to enter an event (usually: sub-goals of earlier events satisfied) |
| **action** | an entry in an event's action catalog: a parameterised prompt plus declared inputs and outputs |
| **option** | an action instance (action + parameters) proposed to the user in a turn |
| **turn** | one cycle: state → options → choice → step → observation → facts → checks |
| **step** | one executed action: a generated script, its runs (attempts), outputs and record |
| **observation** | the structured result of a step (outputs, metrics, figures, logs) |
| **fact** | a structured statement about the data or results, citing the artefact it comes from |
| **test lock** | the mechanism that keeps the test partition unreadable until the `test` event is unlocked |
| **event log** | the append-only record of everything that happens (`.mlca/log/events.jsonl`); the project state is rebuilt from it |
| **branch** | an alternative line of steps starting from an earlier record in the event log |
| **roles** | **Navigator** (proposes options, extracts facts, classifies scope), **Worker** (writes the step script and repairs it), **Inspector** (reads figures with a vision model), **Illustrator** (image generation for diagrams; never in the analysis path) |
| **usage ledger** | per-request record of tokens, cost and latency by role, event and step |
| **egress log** | per-request record of what was sent to a model provider |

---

## 3. Invariants (each needs code plus a test)

| ID | Invariant | Enforced in | Status (2026-10-07) |
|---|---|---|---|
| I1 | The event log is append-only. Each record carries `prev_hash` (sha256 of the previous line), and `mlca log verify` detects any edit | `mlca/log/store.py` | ✅ `log/store.py` (+R1) · `tests/unit/test_store.py` |
| I2 | Project state is a pure function of the event log, so replay gives an identical state | `mlca/log/replay.py` | ✅ `log/replay.py: replay` · replay/`replay --verify` in `tests/integration/test_default_path.py` |
| I3 | An event can be entered only if its gate passes. Otherwise a `GateBlocked` record is written and nothing runs | `mlca/engine/gates.py` | ✅ MCP M0: `tests/integration/test_invariants.py`; MCP guard/bypass paths in `tests/mcp/`. |
| I4 | A sub-goal is satisfied only by its check (or by an explicit `user_confirm` check, logged as a human decision). Model output can never mark a sub-goal satisfied | `mlca/engine/checks.py` | ✅ MCP M0: `tests/integration/test_invariants.py`; MCP guard/bypass paths in `tests/mcp/`. |
| I5 | Options are always instances of the current event's action catalog. The engine validates every option, and an invalid Navigator output gets one repair attempt, then falls back to the template's `default_options` | `mlca/engine/options.py` | ✅ MCP M0: `tests/integration/test_invariants.py`; MCP guard/bypass paths in `tests/mcp/`. |
| I6 | The custom option is appended by the engine, never by the Navigator. A custom instruction passes the scope guard (two layers) before any code is generated | `mlca/engine/scope_guard.py` | ✅ MCP M0: `tests/integration/test_invariants.py`; MCP guard/bypass paths in `tests/mcp/`. I6: brain mode deliberately skips semantic layer 2. |
| I7 | The test partition is unreadable to step scripts until `TestUnlocked` is in the event log; enforcement level recorded (section 7.4) | `mlca/sandbox/` | ✅ `sandbox/vault.py`, `sandbox/bwrap.py`, `api.py: unlock_test` (+R7, R8) · `tests/integration/test_test_lock.py`, `test_sandbox.py` |
| I8 | Every step is a standalone script that reads only declared inputs and writes only to its own step folder. Step folders are immutable after `StepCompleted` | `mlca/runner/` | ✅ MCP M0: `tests/integration/test_invariants.py`; MCP guard/bypass paths in `tests/mcp/`. |
| I9 | Every fact cites an existing artefact (path + sha256); facts without a valid citation are rejected | `mlca/engine/facts.py` | ✅ MCP M0: `tests/integration/test_invariants.py`; MCP guard/bypass paths in `tests/mcp/`. |
| I10 | Every model request writes one usage record and one egress record; raw data rows are never sent unless `privacy.allow_sample_rows: true` | `mlca/llm/client.py` | ✅ `llm/client.py`, `llm/usage.py`, `llm/egress.py` · usage == egress lines in `test_default_path.py`; real providers untested |
| I11 | Preprocessing transforms are fitted only on the training partition, so fitting on validation or test is a check failure (section 7.4.4) | `templates/*/checks.py` + runtime helper | ✅ `mlca_runtime/__init__.py: fit_record`, `engine/checks.py` (`fit_on_train_only`), `runner/static_checks.py` (+R10) · `tests/unit/test_scientific_guards.py` |

---

## 4. Architecture

```
                         ┌─────────────────────── mlca core (Python) ─────────────────────────┐
 clients                 │                                                                     │
 ┌──────────────┐  calls │  engine/      turn loop, gates, options, scope guard, facts, checks  │
 │ mlca CLI     │ ─────► │  templates/   loader + validator for workflow templates             │
 │ (headless)   │        │  log/         event log store, schemas, replay, branches            │
 │ mlca TUI     │ ◄───── │  roles/       navigator, worker, inspector, illustrator + prompts   │
 │ (Textual)    │ events │  llm/         provider clients, structured output, usage, egress    │
 │ [later] RPC  │        │  runner/      step script execution (subprocess), artefact capture  │
 │ server for   │        │  sandbox/     bubblewrap isolation, audit hook, test lock vault     │
 │ Ink/Electron │        │  project/     init, data inventory, project env (uv), config         │
 └──────────────┘        │  report/      methods/provenance, figure index, usage report        │
                         └─────────────────────────────────────────────────────────────────────┘
                                         │ executes
                                         ▼
                 <project>/.mlca/env  (separate Python env, created with uv)
                 + mlca_runtime helper package (save_figure, record_metric, ...)
```

Key decisions:

- **Execution model: one fresh subprocess per step attempt**, running a standalone script. There is no persistent kernel. Reason: every step must be replayable as a numbered script (I8, I2). From Hermes' kernel the plan takes the process-group kill on timeout, environment scrubbing, output caps and framed result reporting (section 9), not the persistent namespace.
- **Two Python environments:** MLCA's own (the tool), and the project's (the analysis). They are never the same, so ML package versions in a project are pinned and recorded independently of the tool.
- **All front ends call one API:** `mlca.api.Session` (section 7.9). The CLI and TUI are thin. A later JSON-RPC server (P9) exposes the same methods, with the event-log records as the event stream.

---

## 5. Repository layout (target state after P8)

> **Status:** ✅ built as below, with these differences:
> - **Added:** `src/mlca/runner/verify.py` (`replay --verify`), `src/mlca/distribution.py`, `src/mlca/web.py`, `installers/`, `packaging/` (npm, homebrew, `NAME`), `.github/workflows/`, `scripts/` (`make_logo.py`, `prime_test_cache.py`, release helpers), `docs/prompts/`, `docs/install.md`, `docs/releasing.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/HANDOFF.md`, `assets/logo.txt`, `assets/logo_source.png`.
> - **Not built:** `roles/illustrator.py` (P9); `templates/*/checks.py`, because no template needs custom checks yet; `tests/integration/test_golden_anemia.py` and `tests/fixtures/tiny_tabular.csv` (replaced by `tests/fixtures/make_synthetic.py` and the `tests/integration/` suite).

```
mlca-revized/
  plan.md                         this file
  README.md                       user-facing: install, first run, commands
  AGENTS.md                       rules for coding agents working on this repo (copy section 0 + build/test commands)
  CHANGELOG.md
  LICENSE                         author-chosen CC-BY-NC-ND-4.0 legal code (D1 resolved)
  THIRD_PARTY_NOTICES.md          attribution for every copied file (section 9)
  pyproject.toml                  package "mlca", Python >=3.11, build backend hatchling, managed with uv
  uv.lock
  assets/
    logo.png                      black-and-white logo (P7); derived from legacy ml-copilot-agent.png only if the author agrees (D5)
    banner.txt                    block-letter "MLCA" terminal banner (P7)
  docs/
    architecture.md  event-log.md  templates.md  security-model.md  providers.md  lineage.md  DECISIONS.md
  src/
    mlca/
      __init__.py                 __version__
      __main__.py                 python -m mlca → cli
      api.py                      Session facade used by all clients (7.9)
      config.py                   user config + project config loading/validation (7.6)
      paths.py                    all filesystem locations in one place
      errors.py
      log/
        schema.py                 pydantic models for every record type (6.1)
        store.py                  append, read, hash chain, file lock
        replay.py                 fold records → ProjectState (6.2)
        branches.py               branch heads, checkout, path-from-root
      templates/
        model.py                  pydantic models for template/event/action/check specs (6.3)
        loader.py                 load + validate a template directory
        registry.py               built-in templates + user templates dir
      engine/
        turn.py                   the turn loop (7.1)
        gates.py
        checks.py                 built-in check types + template checks.py loader (7.2)
        options.py                option validation, fallback, engine-appended options (7.1)
        scope_guard.py            two-layer guard for custom instructions (7.3)
        facts.py                  fact validation and storage
        state_view.py             builds the compact context sent to roles
      roles/
        base.py
        navigator.py              propose_options / extract_facts / classify_scope / summarise_session
        worker.py                 write_script / repair_script
        inspector.py              describe_figure (vision) [P7]
        illustrator.py            generate_image [P9]
        prompts/
          navigator_options.md  navigator_facts.md  navigator_scope.md  navigator_recap.md
          worker_write.md  worker_repair.md  inspector_figure.md
      llm/
        client.py                 LLMClient interface, request wrapper writing usage + egress (I10)
        structured.py             JSON-schema output, validate with pydantic, one repair retry
        providers/
          openai_api.py           OpenAI API key (OPENAI_API_KEY)
          openrouter.py           OpenRouter (OPENROUTER_API_KEY), OpenAI-compatible
          openai_compatible.py    any base_url + key (local servers etc.)
          fake.py                 scripted responses for tests (7.6.4)
        pricing.py                pricing table lookup (user-editable pricing.yaml)
        usage.py                  usage ledger writer + aggregations
        egress.py                 egress log writer + payload classifier
      runner/
        run_step.py               write script, static checks, execute, collect (7.4)
        static_checks.py          AST checks before execution
        process.py                subprocess with process group, timeout, output caps, env scrub
        artefacts.py              hash + record outputs, read runtime manifest
      sandbox/
        bwrap.py                  Linux bubblewrap command builder (level A)
        audit_hook.py             source of the sitecustomize audit hook (level B)
        vault.py                  test partition encryption / unlock (7.4.3)
        level.py                  detect and report enforcement level
      project/
        init.py                   create .mlca/, register data, inventory, create env
        inventory.py              data inventory (pandas, read-only)
        env.py                    uv venv + base requirements + lock + package requests
        files.py                  materialised views: scripts/, figures/, tables/, PROJECT_LOG.md
      report/
        provenance.py             artefact → step → script → run → model calls
        methods.py                methods draft from the event log (template-driven text, no model)
        figure_index.py
        usage_report.py           totals per role/event/step; retries; human interventions
      cli/
        main.py                   Typer app (7.8)
      tui/
        app.py                    Textual app (7.10)
        screens/ welcome.py onboarding.py project.py brief.py template_pick.py main.py report.py
        widgets/ event_graph.py subgoals.py options.py log_stream.py facts.py status_bar.py
        banner.py
    mlca_runtime/                 tiny helper package installed into each project env (7.5)
      __init__.py                 save_figure, save_table, record_metric, record_fact_candidate, inputs, output_dir, fit_record
      style.py                    applies the project figure style
  templates/
    tabular_classification/
      template.yaml
      events/   onboard.yaml data.yaml eda.yaml split.yaml preprocess.yaml features.yaml model.yaml validate.yaml test.yaml interpret.yaml report.yaml
      actions/  <action_id>.yaml (one per action; prompt + inputs + outputs)
      checks.py                   template-specific checks (optional)
    survival/                     P8
  styles/
    default.mplstyle
    palette.yaml                  colours by role (e.g. train/val/test, model families)
  tests/
    unit/ ...                     one test module per source module
    integration/
      test_golden_anemia.py       fake-provider end-to-end run (section 11)
    fixtures/
      fake_llm/anemia_run.yaml    scripted model responses for the golden run
      tiny_tabular.csv            synthetic data (generated, committed)
```

**Project folder** created by `mlca init` (target state):

```
<project>/
  .mlca/
    project.yaml          project id (ULID), created_at, template id + version, data registry, config overrides
    log/events.jsonl      the event log (source of truth)
    log/branches.json     branch name → head record id; current branch
    state.json            cache of replayed state for the current branch (deletable; rebuilt from the log)
    env/                  project Python env (uv)  + requirements.lock
    steps/<step_id>/      immutable step folders (one per step; see 7.4)
    vault/test.enc        encrypted test partition (after split)
    data/splits/          train.parquet, val.parquet, split_manifest.csv (+ sha256)
    llm/                  optional stored request payloads (privacy.store_payloads)
    usage.jsonl           usage ledger
    egress.jsonl          egress log
  scripts/  NN_<event>_<action>.py      materialised view of the current branch (regenerated)
  figures/  tables/  reports/            materialised views (copies/links of step outputs)
  PROJECT_LOG.md                          human-readable rendering of the current branch
```

Materialised views are regenerated from the event log and step folders by `mlca.project.files.materialise()`. They are never edited by the engine in place, and user edits to them are detected (hash mismatch) and reported, not silently overwritten.

---

## 6. Data model

All models are pydantic v2. IDs are ULIDs (`python-ulid`). Timestamps are UTC ISO 8601.

### 6.1 Event-log record

> **Status:** ✅ `log/schema.py`. 🔁 Extra record types (R2), the `head.json` checkpoint (R1), and `BriefRecorded.columns` (R6).

Common envelope (`mlca/log/schema.py`):

```python
class Record(BaseModel):
    id: str                 # ULID
    ts: datetime
    type: RecordType        # enum below
    parent_id: str | None   # previous record on this branch (None for the first record)
    branch: str             # branch name at write time
    session_id: str
    actor: Literal["engine", "user", "navigator", "worker", "inspector", "illustrator"]
    event_id: str | None    # current workflow event, if any
    step_id: str | None
    payload: dict           # validated against the per-type payload model
    prev_hash: str          # sha256 of the previous LINE in the file (file order, across branches)
```

Record types (one payload model each):

| Type | Payload (main fields) |
|---|---|
| `ProjectCreated` | project_id, mlca_version, template_id, template_version, template_sha256 |
| `DataRegistered` | name, original_path, sha256, size, read_only=True |
| `InventoryRecorded` | per file: rows, columns, dtypes, missing counts, sha256 of inventory json |
| `BriefRecorded` | answers to brief questions (verbatim user text) |
| `SessionStarted` / `SessionEnded` | client (cli/tui), mlca_version, config hash (no secrets) |
| `EventEntered` | event_id, via (`start`/`next`/`loop`/`goto`) |
| `GateBlocked` | target event_id, failing conditions |
| `OptionsProposed` | options (list of Option), source (`navigator`/`fallback`), navigator_request_id |
| `OptionChosen` | option id, or `custom` |
| `CustomInstructionSubmitted` | verbatim text |
| `ScopeDecision` | layer (1/2), decision (`in_scope`/`other_event`/`reject`), target_event, reason |
| `StepStarted` | step_id, action_id, params, declared inputs/outputs, script number NN |
| `ScriptWritten` | attempt n, script sha256, path, worker_request_id |
| `StaticCheckFailed` | attempt n, violations |
| `RunFinished` | attempt n, exit status, duration, stdout/stderr tail (capped), sandbox level |
| `StepCompleted` | step_id, outputs (path, sha256, kind), metrics, figures |
| `StepFailed` | step_id, attempts, last error summary |
| `FactRecorded` | key, value, unit, source artefact path + sha256, step_id |
| `FactRejected` | candidate, reason |
| `SubgoalChecked` | subgoal_id, check type, passed, detail |
| `UserConfirmed` | subgoal_id or decision id, verbatim note |
| `TestUnlocked` | confirmation text, steps allowed to read test |
| `PackageRequested` / `PackageApproved` / `PackageDenied` | package spec, reason |
| `BranchCreated` / `BranchCheckedOut` | name, from_record_id |
| `ScriptEditedByUser` | step_id, old/new sha256 (detected on materialised views) |
| `Note` | free text from user |

The usage and egress records live in their own files (`usage.jsonl`, `egress.jsonl`) and are linked by `request_id`. This keeps the event log small. The event log stores `navigator_request_id` / `worker_request_id`.

### 6.2 Project state (replay output)

> **Status:** ✅ `log/schema.py: ProjectState`, `log/replay.py: replay`. Added: `columns`, `generations` (loop invalidation), `split`, `lock_sha256`, `runtime_sha256`.

`ProjectState`: template id/version, current event, event statuses (`locked`/`open`/`done`), sub-goal statuses with last check detail, facts (key → Fact), steps (ordered, with outputs), artefact index (path → sha256, step), test lock status, pending options, counts (turns, retries, custom instructions, rejections, user confirmations, user edits). `replay(records_on_branch) -> ProjectState` is pure: no filesystem access and no clock.

### 6.3 Workflow template format

> **Status:** ✅ `templates/model.py`, `templates/loader.py`; templates in `templates/tabular_classification/`, `templates/survival/`. 🔁 `output_exists.any_of`, action `role`, action `builtin` (R4, R5). Content is still DRAFT (D2).

`templates/<id>/template.yaml`:

```yaml
id: tabular_classification
version: 0.1.0
title: Tabular classification
description: Binary or multiclass classification on one tabular dataset.
brief_questions:                      # asked at project creation; answers stored verbatim
  - id: aim
    text: In one or two sentences, what do you want to predict, and why?
  - id: target
    text: Which column is the target (if known)?
  - id: unit
    text: What does one row represent (patient, sample, visit...)?
events: [onboard, data, eda, split, preprocess, features, model, validate, test, interpret, report]
transitions:                          # allowed moves besides 'next' in list order
  loops:   [{from: validate, to: [preprocess, features, model]}]
  goto:    []                         # free jumps (none by default)
style: default                        # figure style in styles/
default_runtime_packages: [numpy, pandas, scipy, scikit-learn, matplotlib, seaborn, pyarrow]
```

`templates/<id>/events/<event>.yaml`:

```yaml
id: data
title: Data
goal: Understand what the data are, what one row is, and how the target is defined.
gate:                                  # all must pass to enter
  - event_done: onboard
subgoals:
  - id: target_identified
    text: Target column identified and its classes counted
    check: {type: fact_present, key: target.column}
  - id: schema_recorded
    text: Column types and missingness recorded
    check: {type: output_exists, action: audit_schema, output: schema.json}
  - id: unit_of_analysis
    text: Unit of analysis confirmed
    check: {type: user_confirm}
actions: [audit_schema, count_target, check_duplicates, inspect_target_definition]
default_options: [audit_schema, count_target, check_duplicates]   # used when Navigator output is invalid
done_when: all_subgoals                 # or a list of subgoal ids
custom_scope:
  description: Questions about the raw data files, their columns, types, missingness, duplicates and target definition.
  deny_patterns: ['(?i)\b(train|fit)\b.*\bmodel\b', '(?i)\btest (set|split|partition)\b']
  readable_inputs: [registered_data]
max_options: 4                          # options shown, excluding engine-appended ones
```

`templates/<id>/actions/<action>.yaml`:

```yaml
id: audit_schema
event: data
title: Audit columns, types and missingness
params:                                  # Navigator fills these; engine validates types/enums
  dataset: {type: data_ref}
prompt: |                                # parameterised prompt given to the Worker
  Load {dataset} read-only. Record each column's dtype, number of unique values and missing count.
  Save schema.json with these fields and a bar chart of missing counts per column.
inputs: [{ref: "{dataset}"}]
outputs:
  - {name: schema.json, kind: table, required: true}
  - {name: missingness.png, kind: figure, required: false}
fact_candidates: [n_rows, n_columns, missing.total]
reads_test: false
timeout_s: 300
```

Built-in check types (`mlca/engine/checks.py`): `event_done`, `fact_present` (key, optional predicate), `output_exists` (action, output), `artefact_hash_recorded`, `metric_present` (name, split), `figure_count` (min), `split_frozen` (split manifest + hash recorded and vault created), `fit_on_train_only` (I11; reads fit records from the runtime manifest), `test_unlocked`, `user_confirm`, `template_check` (calls a function in the template's `checks.py`, given read-only state and artefact paths; must return `(passed, detail)`).

**Template content is the author's work (section 12, D2).** In P2 the agent ships `tabular_classification` with complete *structure*, and with event goals, sub-goals and action prompts marked `# DRAFT – author to finalise`, kept short. The golden test (section 11) must pass with the draft. The author then rewrites the content without code changes.

### 6.4 Option (Navigator output, validated)

> **Status:** ✅ `engine/options.py: Option, validate, fallback`. 🔁 Completed events offer next, unrun supporting actions and scoped custom (R12, author-approved 2026-10-07).

```python
class Option(BaseModel):
    id: str                       # "1".."4"
    action_id: str                # must be in current event's actions (I5)
    params: dict                  # validated against the action's params
    title: str                    # <= 80 chars
    why_now: str                  # <= 200 chars, must reference state (fact key or sub-goal id)
    advances: list[str]           # sub-goal ids of the current event that are not yet satisfied (or [] for loop-back options)
    expected_outputs: list[str]   # subset of the action's outputs
    est_cost_usd: float | None    # filled by the engine from the pricing table, not by the model
```

Validation rejects options whose action is not in the catalog, whose params fail, whose `advances` names a satisfied or unknown sub-goal, or that duplicate a completed step with identical params. Engine-appended options, in this order after the model's options:
- `next` (shown only when the current event is done and the next gate passes);
- `loop:<event>` (allowed loops when the current event is `validate`);
- `custom` (always last).

---

## 7. Subsystem specifications

### 7.1 Turn loop (`engine/turn.py`)

> **Status:** ✅ `engine/turn.py: execute`, `api.py: Session.options/choose/custom`; budgets in `llm/client.py: _budget`. 🟡 Navigator fact extraction and Inspector notes untested with real models.

```
state = replay(branch)
if state.pending_options is None:
    ctx = state_view.build(state, template)          # compact: event spec, sub-goal status, facts, last observation summary, artefact list
    options = navigator.propose_options(ctx)         # structured output; validated (I5); fallback to default_options
    log OptionsProposed
choice = client.ask(options + engine options)        # CLI arg or TUI selection
log OptionChosen / CustomInstructionSubmitted
if custom: scope_guard (7.3) → may end turn with reject or offer move to other event
if next/loop: gates.check → EventEntered or GateBlocked; end turn
step = runner.run_step(action, params, state)        # 7.4: worker writes script, static checks, run, repair ≤ max_attempts
observation = artefacts + metrics + figures + stdout tail
facts = navigator.extract_facts(observation, action.fact_candidates)   # each validated (I9)
[P7] inspector.describe_figure for each new figure → stored as observation note (not a fact unless it cites a table/metric)
checks.run_all(current event)                         # SubgoalChecked records
materialise views; return TurnResult
```

Budgets (config, defaults): `worker.max_attempts: 3`; `turn.max_cost_usd: 1.00`, which aborts the turn before the next model call if it would exceed; `session.max_cost_usd: 10.00`. A budget stop is logged and shown to the user.

### 7.2 Gates and checks

> **Status:** ✅ `engine/gates.py`, `engine/checks.py`; `user_confirm` via `api.py: confirm`. ✅ I3/I4 dedicated regressions in `test_invariants.py` (MCP M0).

- Gates are lists of check specs evaluated against `ProjectState` (+ artefact files for file-based checks). Evaluation results are logged.
- Checks run after every step and on `mlca status --recheck`. A check never calls a model.
- `user_confirm` is satisfied only by an explicit user action (`mlca confirm <subgoal> "<note>"` or the TUI confirm dialog). The note is stored verbatim.

### 7.3 Scope guard (`engine/scope_guard.py`)

> **Status:** ✅ `engine/scope_guard.py: layer_one`, `roles/navigator.py: classify_scope`, `api.py: custom`. ✅ Layer-1 zero-model-call tests in `test_invariants.py` and `tests/mcp/test_guards.py`. Brain mode skips semantic layer 2 by design.

Layer 1 (deterministic, no model):
- reject if the text matches any `deny_patterns` of the current event;
- reject if it references a path not in the event's `readable_inputs` / prior step outputs;
- reject if it references the test partition while locked;
- reject if it is empty or longer than 2,000 characters.

Layer 2 (Navigator `classify_scope`, structured output `{decision: in_scope|other_event|reject, target_event?, reason}`):
- `in_scope`: run as a step with the built-in action `custom` (prompt = the user's text inside a fixed wrapper that restates the event's scope and the I8 rules);
- `other_event`: show "This belongs to <event>". Offer to move there if gates allow, otherwise show what is missing;
- `reject`: show the reason.

Both layers write `ScopeDecision`. Layer 1 runs first, and a layer-1 rejection never reaches a model.

### 7.4 Step execution (`runner/`, `sandbox/`)

> **Status:** ✅ `runner/run_step.py`, `runner/process.py`, `runner/static_checks.py`, `sandbox/bwrap.py`, `sandbox/audit_hook.py`, `sandbox/vault.py`, `engine/split.py: freeze`. 🔁 R7–R11. The reviewer verified level A: original data, vault and key folder not visible; environment scrubbed; network blocked.

#### 7.4.1 Step folder

`.mlca/steps/<step_id>/`, with `step_id` = `NN_<event>_<action>` plus a short ULID suffix:
- `script.py` (final);
- `attempts/<n>/script.py`, `stdout.txt`, `stderr.txt`;
- `inputs.json` (declared inputs with sha256);
- `outputs/` (everything the script writes);
- `manifest.json` (written by `mlca_runtime`);
- `record.json` (engine summary).

The folder becomes read-only (chmod) after `StepCompleted`.

#### 7.4.2 Execution

`process.py`:
- `subprocess.Popen([project_env_python, script], cwd=step_dir, env=scrubbed_env, start_new_session=True)`;
- timeout from the action spec; on timeout or interrupt, `os.killpg` the group;
- stdout and stderr capped at 1 MB each, with the tail kept for the log;
- `scrubbed_env` keeps only `PATH`, `HOME` (set to a temp dir), `LANG`, `MPLBACKEND=Agg`, `PYTHONHASHSEED=0`, plus `MLCA_*` variables. It removes every variable matching `*KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*`.

`static_checks.py` runs before execution and makes an AST pass that rejects:
- open/read calls on literal paths outside the declared inputs, the step dir and `mlca_runtime` paths;
- any reference to `.mlca/vault` or the original data path after the split;
- `subprocess`, `os.system`, `socket`, `requests`, `urllib`, `http` imports, unless the action allows network;
- writes outside `outputs/`.

Violations go back to the Worker as repair input (`StaticCheckFailed`).

The Worker contract: the input is the rendered action prompt plus a fixed preamble (inputs available via `mlca_runtime.inputs()`, write only via `mlca_runtime` helpers or into `mlca_runtime.output_dir()`, no network, set seeds, the list of installed packages). The output is exactly one Python script in a fenced block. Repair input: the previous script, a truncated traceback (≤ 4,000 chars) and the static-check violations.

#### 7.4.3 Test lock

Split procedure (built-in, not model-written, so the lock cannot be bypassed by generated code):
- the `split` event's actions only choose parameters (method `stratified`/`group`/`time`, fractions, seed, group column);
- the engine function `mlca.engine.split.freeze()` writes `split_manifest.csv` (row id → partition) and `train.parquet` / `val.parquet`;
- it encrypts the test rows to `.mlca/vault/test.enc` (Fernet, `cryptography`), with the key at `~/.local/share/mlca/keys/<project_id>.key` (mode 600, outside the project);
- it records all sha256 values.

After `freeze`, steps declare inputs `train`/`val` (and `test` only after unlock), and the registered original data are no longer a readable input for any step.

`TestUnlocked`:
- the user must type a confirmation phrase in the `test` event;
- the engine decrypts to `.mlca/data/splits/test.parquet` for the duration of the declared `reads_test: true` steps only, and deletes it afterwards;
- every read is logged;
- re-unlocking is allowed but logged as a separate `TestUnlocked` with a reason, and counted in reports.

Enforcement levels (`sandbox/level.py`, recorded in every `RunFinished`):
- **Level A (Linux with bwrap):**
  - the step runs under `bwrap` with read-only binds of the project env, `mlca_runtime` and the declared input files;
  - a read-write bind of the step folder only;
  - no bind of `.mlca/vault`, the key directory, the original data path (after the split) or `$HOME`;
  - `--unshare-net` unless the action allows network;
  - `--die-with-parent`.
- **Level B (other OS, or bwrap missing):**
  - static checks;
  - a `sitecustomize.py` placed in the step's `PYTHONPATH` that installs `sys.addaudithook` and aborts on `open` events for forbidden paths;
  - the encrypted vault.

  `docs/security-model.md` must state plainly what level B does not stop (C extensions reading files directly, subprocesses if not caught statically).

#### 7.4.4 `fit_on_train_only` (I11)

`mlca_runtime.fit_record(estimator_or_pipeline, X, partition)` records the partition name and the sha256 of `X`'s index for every `fit` call in `manifest.json`. The `preprocess`, `features` and `model` action preambles require using it. The check fails if any fit record names `val` or `test`, or if a fitted object appears in outputs with no fit record.

### 7.5 `mlca_runtime` (helper package in the project env)

> **Status:** ✅ `src/mlca_runtime/__init__.py` (plus `save_model`, `save_json`, `index_sha256`), snapshotted per project into `.mlca/runtime/` (R13).

Installed into `<project>/.mlca/env` at init (editable path install from the MLCA package data, version-pinned). API:
- `inputs() -> dict[str, Path]`
- `output_dir() -> Path`
- `save_figure(fig, name, caption)` → PNG at 300 dpi + SVG, applies style
- `save_table(df, name, caption)` → CSV + parquet
- `record_metric(name, value, split, ci=None)`
- `record_fact_candidate(key, value, unit=None, source=name_of_saved_table_or_metric)`
- `fit_record(...)`
- `set_seed(seed)`

All of these append to `manifest.json`, the only machine-readable link between a script and the engine.

### 7.6 Providers, roles, usage and egress (`llm/`)

> **Status:** ✅ `llm/client.py`, `llm/structured.py`, `llm/usage.py`, `llm/egress.py`, `llm/pricing.py`, `llm/providers/{openai_api,openrouter,openai_compatible,fake}.py`; config in `config.py`. 🟡 Real OpenAI/OpenRouter calls not yet run (live tests not written). ⬜ 7.6.6 (ChatGPT login, opencode free models) still waits for the author.

#### 7.6.1 Configuration

- **User config:** `~/.config/mlca/config.yaml`, created by onboarding.
- **Project override:** `.mlca/project.yaml: config:`.
- **Keys:** environment only (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `MLCA_<NAME>_API_KEY` for custom providers). Config may name the variable, never the value.

```yaml
providers:
  openai:      {kind: openai_api,  api_key_env: OPENAI_API_KEY}
  openrouter:  {kind: openrouter,  api_key_env: OPENROUTER_API_KEY, base_url: https://openrouter.ai/api/v1}
  local:       {kind: openai_compatible, base_url: http://localhost:11434/v1, api_key_env: null}
roles:
  navigator:   {provider: openai,     model: "<set at onboarding>", temperature: 0}
  worker:      {provider: openai,     model: "<set at onboarding>", temperature: 0}
  inspector:   {provider: openrouter, model: "<vision model>"}            # P7
  illustrator: {provider: openrouter, model: "<image model>"}             # P9
privacy:
  allow_sample_rows: false      # I10
  store_payloads: true          # keep request/response JSON in .mlca/llm/
budgets: {turn_max_usd: 1.0, session_max_usd: 10.0, worker_max_attempts: 3}
```

#### 7.6.2 Client interface

```python
class LLMClient(Protocol):
    def complete(self, role: str, messages: list[Message], *, schema: type[BaseModel] | None = None,
                 images: list[Path] | None = None, context: RequestContext) -> LLMResult: ...
# LLMResult: text | parsed model, usage (input, output, cached tokens), provider cost if returned, latency, request_id
```

- `openai_api`, `openrouter` and `openai_compatible` all use the official `openai` Python SDK (`base_url` differs).
- Structured output uses `response_format={"type": "json_schema", ...}` when the provider/model supports it; otherwise JSON in the text, then a pydantic validation and one repair request (`llm/structured.py`).
- Retries: exponential backoff on 429/5xx, at most 3, each logged as its own usage record.

#### 7.6.3 Usage ledger and pricing

`usage.jsonl` holds one line per request: request_id, ts, role, provider, model, event_id, step_id, attempt, input/output/cached tokens, cost_usd, cost_source (`provider` when OpenRouter returns cost in `usage`; `pricing_table` otherwise; `unknown`), latency_ms, status. `pricing.yaml` lives in the user config dir, is user-editable and ships with an empty default. Costs are never invented: unknown stays `unknown`.

#### 7.6.4 Egress log

`egress.jsonl` holds one line per request: request_id, role, provider, model, bytes sent, sha256 of the payload, and content categories. The categories come from the builder that assembled the messages, not from guessing: `template_spec`, `facts`, `inventory_summary`, `script`, `traceback`, `figure_image`, `sample_rows`, `user_text`.

`state_view.build` and the role prompt builders tag every section they add. If `sample_rows` would be included while `allow_sample_rows` is false, the builder raises an exception.

#### 7.6.5 Fake provider

`fake.py` reads a YAML script of responses keyed by `(role, call index)` or by a matcher (role + event + action). It returns fixed usage numbers. It is used by all offline tests and the golden run.

#### 7.6.6 Later providers (P9, not before)

- **ChatGPT account login:** the reference is opencode `packages/opencode/src/plugin/openai/codex.ts`. Reimplement in Python only after the author confirms the provider's terms allow it.
- **Free models listed by opencode:** opencode reads the provider catalogue from models.dev and, without a key, keeps only the zero-cost models of its `opencode` provider, using the API key `"public"`. See `packages/opencode/src/provider/provider.ts` around line 185 and `packages/core/src/plugin/provider/opencode.ts` around line 175. Before implementing an equivalent, the author must confirm that its terms allow use from another harness. Until then, use free models through OpenRouter or a local `openai_compatible` server.
- **Claude subscriptions:** do not implement. As far as we know, Anthropic does not allow consumer subscriptions in third-party harnesses; use API keys.

### 7.7 Project lifecycle (`project/`)

> **Status:** ✅ `project/init.py`, `project/inventory.py`, `project/env.py`, `project/files.py`; branches in `log/branches.py` + `api.py: branch/checkout` (re-check after a branch, R12). 🔁 Column resolution (R6), lazy session records (R3). 🟡 The Navigator recap on open is untested.

`mlca init <path>`:
1. Refuse if `.mlca/` exists.
2. Create the layout (section 5).
3. Ask for data files (paths). Register each (`DataRegistered`, sha256), without copying data: the registry stores the original path, and steps get read-only access.
4. Run the inventory (`InventoryRecorded`).
5. Choose the template (`registry.list()`).
6. Ask the brief questions (`BriefRecorded`, verbatim).
7. Create the project env with uv (`uv venv .mlca/env`; `uv pip install` the template's `default_runtime_packages` + `mlca_runtime`), write `requirements.lock` (`uv pip freeze`) and record its sha256 in `ProjectCreated`.
8. Enter the first event.

A package request comes from the Worker or the user (`PackageRequested`). It needs a user decision, then `uv pip install`, a new lock and its hash.

**Sessions:**
- `SessionStarted` is written when the CLI or TUI opens a project.
- On open, `navigator.summarise_session` produces a short recap from the last N records ("Last session: …"). It is shown, not logged as a fact.
- If no model is configured, the recap is a deterministic list of the last steps.

**Branches:**
- `mlca branch <name> --from <record_id|step_id>` creates `BranchCreated`, and the new branch's state is the replay up to that record.
- Step folders are shared (immutable), while views are re-materialised per branch.
- `mlca checkout <name>` switches branch.

### 7.8 CLI (`cli/main.py`, Typer)

> **Status:** ✅ `cli/main.py` (all commands listed below, plus R14).

```
mlca                       open TUI in current folder (init wizard if no project)
mlca init [PATH]           create a project (interactive; --data, --template, --brief-file for non-interactive)
mlca status                current event, sub-goals, facts, branch, budget used     [--recheck] [--json]
mlca options               show (or create) the current options                      [--json]
mlca choose N              run option N
mlca custom "TEXT"         submit a custom instruction (scope guard applies)
mlca next | mlca loop EVENT | mlca goto EVENT
mlca confirm SUBGOAL "NOTE"
mlca unlock-test           (only in event 'test'; asks for the confirmation phrase)
mlca branch NAME --from ID | mlca checkout NAME | mlca branches
mlca log [--verify] [--branch NAME] [--json]
mlca replay --verify       re-run every step script of the branch in a fresh env; compare output hashes (figures: compare manifest metrics only)
mlca report [methods|provenance|figures|usage|all]
mlca usage                 usage summary
mlca config [show|edit|check]
mlca doctor                python/uv/bwrap/keys(env present?)/sandbox level
```

Every command except `init` and `config` works headless with `--json` output, which tests and later clients use.

### 7.9 Session API (`api.py`)

> **Status:** ✅ `api.py: Session` (plus `package`, `verify_scripts`, and the state cache keyed on the branch head).

`Session.open(path)`, `.status()`, `.options()`, `.choose(n)`, `.custom(text)`, `.next()`, `.loop(event)`, `.goto(event)`, `.confirm(subgoal, note)`, `.unlock_test(phrase)`, `.branch(name, from_id)`, `.checkout(name)`, `.report(kind)`, `.subscribe(callback)` (receives each new log record). The CLI, TUI and future RPC server call only this API.

### 7.10 TUI (`tui/`, Textual)

> **Status:** ✅ `tui/app.py`, `tui/screens/*`, `tui/widgets/*`, `tui/banner.py`. 🔁 R15. 🟡 Main-screen layout is functional but plain; TUI flows beyond open/quit/readable log are untested.

**Screens:**
1. **Welcome:** banner from `assets/banner.txt`, version, sandbox level, configured roles. Shows "first run" if no user config.
2. **Onboarding:** provider env vars present or missing (never display values), choose models per role (free text + list from the provider's `/models` if available), budgets, privacy switches, then a `doctor` result.
3. **Project:** open an existing project, or init a new one (the `mlca init` steps as forms).
4. **Main:**
   - left: event graph as a vertical list with status icons and the current event highlighted;
   - centre: event goal, sub-goal checklist, numbered options (`1`–`4`, then `n` next, `l` loop, `c` custom);
   - right: facts table;
   - bottom: live log stream of the running step (attempt, stdout tail);
   - status bar: branch, event, turns, session cost/tokens, sandbox level.
5. **Report:** view generated reports. Figures open with the system viewer (`xdg-open`/`open`); paths are shown.

**Keys:** `1`–`4` choose, `n` next, `l` loop, `c` custom, `f` confirm sub-goal, `b` branches, `r` report, `u` usage, `q` quit (writes `SessionEnded`).

### 7.11 Reports (`report/`, no model calls)

> **Status:** ✅ `report/{provenance,methods,figure_index,usage_report}.py` → `reports/generated/` (plus `project_test_exposure.json`).

- **`provenance`:** for every figure, table and metric in the current branch, the chain artefact → step → script (sha256) → run attempt → model requests (ids, models) → inputs (sha256).
- **`methods`:** a deterministic text draft assembled from the template's per-action `methods_text` fields (optional in action YAML), the step params, package versions from the lock and the split parameters. It is labelled "draft generated from the event log".
- **`figures`:** index with captions, step and file.
- **`usage`:**
  - per role, event and step: requests, tokens, cost (with cost_source counts);
  - worker attempts and repair rate;
  - human interventions: choices, custom instructions accepted/rejected, user confirmations, package approvals, user script edits;
  - test unlocks;
  - wall time per step.

---

## 8. Phases

Each phase ends with: tests green (`uv run pytest`), `ruff check` clean, `CHANGELOG.md` and `docs/DECISIONS.md` updated, and a local commit `P<n>: …`. **Done when** lists what will be verified in review.

### P0: repository bootstrap

> **Status:** ✅ done (`8a8a3c9`). `docs/lineage.md` written.
- `git init`; `pyproject.toml` (hatchling; deps: pydantic>=2, typer, textual, rich, pyyaml, python-ulid, openai, cryptography, pandas, pyarrow, filelock; dev: pytest, ruff, pytest-cov); `src/` layout; `uv lock`.
- `README.md` (stub), `AGENTS.md` (section 0 rules + commands), `CHANGELOG.md`, `docs/DECISIONS.md`, `THIRD_PARTY_NOTICES.md` (empty table), `LICENSE` placeholder text "License to be chosen by the author".
- `docs/lineage.md`: map v1 → v2 for the paper's continuity. v1 events (`InitializeEvent`, `ListFilesEvent`, `PreprocessEvent`, `TrainEvent`, `EvaluateEvent`, `PlotEvent`, `DocumentEvent`, `CustomEvent`, `StopEvent` on `master`; plus `LoadDataEvent`, `ClusterEvent`, `SelectModelEvent`, `AnalyzeSurvivalEvent` on `v1.5`) → v2 events/actions. Note the factual difference: v1's preprocessing prompt (`ml_copilot_agent/workflow.py`, `data_preprocessing`) scaled the whole dataset before any train/test split, while v2 forbids fitting before `split` (I11).
- **Done when:** `uv run python -m mlca --version` works; `uv run pytest` runs (0 tests OK).

### P1: event log, schemas, replay, branches

> **Status:** ✅ done (`7a936b4`, hardened in `215a3c4` F6). Tests: `tests/unit/test_store.py`, `tests/integration/test_branching.py`.
- `log/schema.py`, `log/store.py`, `log/replay.py`, `log/branches.py`.
- **Tests:**
  - append/read round trip;
  - hash chain detects an edited line (I1);
  - replay determinism: the same records give an equal state (I2);
  - branch from an earlier record gives a state equal to the replay up to that record;
  - concurrent append protected by file lock.
- **Done when:** `mlca log --verify` on a fixture log reports OK and reports the exact line of a tampered record.

### P2: workflow templates, checks, gates

> **Status:** ✅ done (`b74e084`, `bc6b254` F3). Tests: `tests/unit/test_template_loader.py`, `test_checks.py`, `tests/integration/test_alternatives.py`. 🟡 The five broken-fixture loader tests are partly covered.
- `templates/model.py`, `loader.py`, `registry.py`; `engine/checks.py`, `engine/gates.py`.
- Ship `templates/tabular_classification/` with the full structure and DRAFT content (section 6.3). It must cover all 11 events, at least 2 actions per event (except `onboard`/`report`), and at least one `user_confirm` sub-goal.
- The validator rejects:
  - unknown action ids;
  - actions listed under the wrong event;
  - unknown check types;
  - transitions to unknown events;
  - `reads_test: true` outside `test`/`interpret`/`report`;
  - missing `default_options`.
- **Tests:**
  - each check type on fixture states;
  - gate blocking writes `GateBlocked`;
  - loader error messages name the file and field.
- **Done when:** `mlca templates validate templates/tabular_classification` passes, and 5 deliberately broken fixtures each fail with the right message.

### P3: project init, inventory, project env, runtime helpers

> **Status:** ✅ done (`07e515b`, `548c38a` F5). Tests: `tests/unit/test_init_columns.py`, environment creation in the integration tests.
- `project/init.py`, `inventory.py`, `env.py`, `files.py`; `src/mlca_runtime/`.
- **Tests (env creation is marked `slow` but must run in CI locally):**
  - init creates the layout;
  - the registry stores sha256;
  - the inventory of `tests/fixtures/tiny_tabular.csv` is correct;
  - a project env is created with uv and `import mlca_runtime` works inside it;
  - the lock hash is recorded;
  - re-init is refused.
- **Done when:** `mlca init /tmp/x --data tests/fixtures/tiny_tabular.csv --template tabular_classification --brief-file tests/fixtures/brief.yaml` completes non-interactively, and `mlca status --json` shows event `onboard` or `data`.

### P4: runner, static checks, sandbox, test lock

> **Status:** ✅ done (`39853fb`, portable paths `f98793d`). Tests: `tests/integration/test_sandbox.py`, `test_test_lock.py`, `tests/unit/test_scientific_guards.py`, `test_platform_runtime.py`.
- `runner/*`, `sandbox/*`, `engine/split.py` (freeze).
- **Tests:**
  - timeout kills the process group (a script that spawns a sleeping child);
  - env scrub removes `*KEY*` variables;
  - static checks catch forbidden imports and paths;
  - level A: a script trying to open the vault, the key or the original data after the split fails under bwrap (skip if bwrap is missing);
  - level B: the audit hook aborts `open()` on the vault;
  - split freeze is deterministic for a fixed seed, writes the hashes, and leaves `test.parquet` absent until unlock;
  - unlock exposes the test partition only to `reads_test` steps and removes it after;
  - the step folder is read-only after completion;
  - `fit_on_train_only` fails for a script that fits on `val`.
- **Done when:** these tests pass, and `docs/security-model.md` states levels A/B and their limits.

### P5: LLM layer, usage, egress, fake provider

> **Status:** 🟡 code done (`3bfa0c1`); usage/egress counted in `test_default_path.py`. **MCP M0 update:** deterministic structured repair/fallback, 429 retry and credential-canary persistence tests now pass in `test_invariants.py`. The live provider smoke test remains deferred.
- `llm/*`.
- **Tests:**
  - the fake provider replays a script;
  - structured output validation + one repair;
  - backoff on simulated 429;
  - one usage line and one egress line per request (I10);
  - `cost_source` logic;
  - a builder raises on `sample_rows` when disallowed;
  - no key value ever appears in any written file (grep test over the project dir after a run with a dummy key `sk-test-DO-NOT-LOG`).
- Live smoke test (`@pytest.mark.live`): one tiny structured call per configured provider.
- **Done when:** offline tests pass; the live test passes when the author runs it with real keys.

### P6: roles and the turn loop, headless end to end

> **Status:** 🟡 done (`94cdc06`). Full synthetic path + `replay --verify` pass (`tests/integration/test_default_path.py`). **MCP M0–M4 update:** invalid Navigator output, zero-call scope refusal, invalid facts, Worker repair, budget stop and terminal attempt limits now have offline regressions in `test_invariants.py`, `test_mcp_engine.py` and `tests/mcp/`. The golden run uses synthetic data, not anemia (§11).
- `roles/*` (navigator, worker), `prompts/*.md`, `engine/turn.py`, `options.py`, `scope_guard.py`, `facts.py`, `state_view.py`, `api.py`, `cli/main.py` (all commands in 7.8 except `report`, which comes in P7).
- **Tests:**
  - invalid Navigator options → repair → fallback to `default_options` (I5);
  - engine-appended options appear only when allowed;
  - scope guard layer 1 cases (deny pattern, foreign path, test reference) never call the model (assert zero fake calls);
  - layer 2 decisions;
  - Worker repair loop up to `max_attempts`, then `StepFailed`;
  - facts without a valid citation are rejected (I9);
  - budget stop.
- **Golden test** `tests/integration/test_golden_anemia.py` (section 11) with the fake provider: runs from init to the `report` event.
- **Done when:** the golden test passes offline in under 3 minutes, and `mlca replay --verify` on its project reports all step outputs reproduced.

### P7: TUI, reports, inspector, banner

> **Status:** 🟡 done (`dee81cc`; banner `6dc9309`; F7 `d13bbcb`). Tests: `tests/tui/test_tui.py` (welcome, open, quit, readable log). The "Done when" (author drives anemia through the TUI with real models) is **not yet done**.
- `tui/*`, `report/*`, `roles/inspector.py`, `assets/banner.txt`, `assets/logo.png` (after D5).
- **Tests:**
  - Textual pilot tests: open project, choose option 1, custom rejected with reason, confirm sub-goal, quit writes `SessionEnded`;
  - report generation from the golden project: provenance covers every figure/table/metric, and usage totals equal the sums of `usage.jsonl`;
  - inspector output stored as an observation note, never as a fact unless it cites a table/metric.
- **Done when:** the author can run `mlca` in a fresh folder, complete onboarding and drive the anemia project through the TUI with real models.

### P8: second template and hardening

> **Status:** 🟡 done (`c555616` … `f56c9ef`). Survival template structure and column resolution are tested; **a full survival workflow run is not.** Branch UX, `ScriptEditedByUser` detection and `mlca doctor` exist.
- `templates/survival/` (DRAFT content; needs `lifelines` in the template's runtime packages).
- Branch UX in the TUI; `ScriptEditedByUser` detection; `mlca doctor`.
- `docs/templates.md` (how to write a template), `docs/providers.md`.
- **Done when:** a golden survival run with the fake provider passes (synthetic survival fixture), and a branch created at a `model` step yields two different `model` results whose reports both regenerate from the log.

### P9: later (each needs the author's go-ahead; do not start without it)

> **Status:** 🔁 partly started on the author's go-ahead: **distribution** done and prepared, not published (R16; prompt 02; `b371aa5` … `61cb041`). It includes `mlca web` (browser TUI through `textual-serve`). ⬜ Still open: general frontend RPC, Ink/Electron clients (the stdio MCP server is implemented), Illustrator, ChatGPT login, opencode free models.
- JSON-RPC server over stdio exposing `api.Session` (records as notifications); reference architecture: Hermes `tui_gateway/` (Python) ↔ `ui-tui/` (Ink/React) and `apps/desktop/` (Electron).
- Ink TUI and Electron desktop clients in `clients/`; banner rendering style from opencode `packages/tui/src/logo.ts` + `component/logo.tsx` (copy with attribution).
- `npx mlca` launcher: an npm package that installs/updates the Python core with uv and starts it (reference: Hermes `apps/bootstrap-installer/`, deepseek `npx @deepseek-ai/dsh`).
- Illustrator role (image generation via OpenRouter image models), only for diagrams and graphical abstracts, with outputs in `reports/illustrations/`, never as analysis artefacts.
- ChatGPT-account login and free models (7.6.6), only after the terms check.
- Web client hosted on Firebase (static), only as a front end to a locally running core.

### P10: evaluation instrumentation (metrics for the paper; do before the author's first VM test)

> **Status:** ⬜ planned 2026-10-07. Authorised by the author: do it now, before M7.

**Purpose.** MLCA itself should record, with minimal extra tracking, the agent-level evidence the reviewers ask for. The comment IDs refer to `ES/submission2/review1/review1_es_working.md` in the paper repository:
- completion, failures and recovery: R1-2a, R2-2;
- interventions and human effort: R1-3, R1-4, R2-2;
- time, calls, tokens and cost: R1-4;
- environment and model identity: R1-2b, R1-4;
- what was sent to the provider: R1-6b;
- traceability: R1-7f.

Most raw signals already exist in the event log, `usage.jsonl` and `egress.jsonl`. P10 adds the missing ones, plus one command that turns a project into a metrics file. Baselines (AutoML, plain LLM) and the planted-flaw task set are paper experiments: they live in `ES/submission2/experiments/` and only *use* these commands.

**Hard rules.**
- Computing metrics never calls a model.
- Every number states its source: `exact` (from records), `derived` (computed from timestamps or counts), `client-reported` (imported from an agent's transcript), or `unavailable`.
- Unknown is never written as zero.

#### P10.1 Run snapshot (R1-2b, R1-4)

> **Status:** ✅ implemented; details and validation in `docs/IMPLEMENTATION_STATUS.md`.
- New record type `RunSnapshot`, written once per session with the first mutating record (next to `SessionStarted`), and at the start of every bench run. It contains:
  - MLCA version, and the git commit when run from a checkout;
  - Python, OS and kernel, CPU model and core count, RAM, and GPU (`nvidia-smi` if present, otherwise `none`);
  - uv and bubblewrap versions; sandbox level;
  - template id, version and sha256; analysis-environment lock sha256;
  - mode (`brain` or `driver`) and client principal;
  - for every configured role: provider kind, model, temperature, max output tokens and base URL host (never keys).
- In `usage.jsonl`, add `model_reported`: the model id the provider returned in its response (it can differ from the configured alias), and `request_settings`: temperature and max tokens actually sent.
- **Test:** the snapshot exists after the first mutation; it contains no secret (credential-canary scan); `model_reported` is filled from a fake response.

#### P10.2 Decision timing and human effort (R1-4, R1-3, R2-2)
- Write timing into the existing decision records:
  - **`OptionChosen` and `CustomInstructionSubmitted`:** `decision_wait_s` (seconds since the matching `OptionsProposed`), and `principal` (already present).
  - **`CustomInstructionSubmitted`:** `chars` and `words` of the instruction.
  - **`ApprovalResolved`:** `wait_s` (since `ApprovalRequested`). For `UserConfirmed` without a request, `wait_s` runs from when the sub-goal first became the only open one.
  - **TUI only:** `active_s`, the time with keyboard or mouse activity while that decision was pending. A gap longer than 120 s counts as idle and is excluded; the cutoff is recorded with the value. CLI and MCP decisions have no `active_s` (`unavailable`); their `decision_wait_s` is an upper bound.
- `ScriptEditedByUser` gains `lines_changed`.
- **Test:** timings are present and non-negative; idle gaps are excluded in a Textual pilot test with simulated keystrokes and a fake clock.

#### P10.3 Failure categories (R2-2, R1-2a)
Every refusal or failure record gets a `category` from a fixed list, set where it is written (not guessed later):
`static_check`, `sandbox_denied`, `runtime_error:<ExceptionType>`, `timeout`, `missing_output`, `fit_rule`, `test_lock`, `scope_layer1`, `scope_layer2`, `gate_blocked`, `invalid_options`, `provider_error`, `budget_stop`, `privacy_refusal`, `abandoned`.

- **Test:** one case per category.

#### P10.4 `mlca metrics` (single project, any mode)
`mlca metrics [--branch B] [--json] [--out FILE]` writes `reports/generated/metrics.json`. All values are computed from the log and ledgers only. Sections:

| Section | Fields |
|---|---|
| `run` | snapshot reference, mode, principal(s), start/end time, wall time, branch, events reached, `completed` (reached `report` with all sub-goals passed) |
| `steps` | count; per step: action, attempts, `first_try_success`, `recovered` (succeeded after at least one failed attempt), final status, compute time |
| `recovery` | steps with failures; recovered automatically (no human action between failure and success); recovered after human action; unrecovered |
| `failures` | counts by P10.3 category |
| `interventions` | by principal: option choices, custom instructions (count, total words), confirmations, approvals requested/granted/declined, test unlocks, package approvals, user script edits (lines) |
| `time` | `llm_s` (sum of request latencies), `compute_s` (sum of run durations), `human_wait_s`, `human_active_s` (when available), `agent_decision_s` (agent principals), `engine_overhead_s` (wall − others, may be approximate) |
| `models` | per role: calls, input/output/cached tokens, cost with `cost_source`; `model_reported` values; for brain mode, `external_agent` tokens from P10.5 when imported, otherwise `unavailable` |
| `egress` | requests and tool results sent out: count, bytes, and counts by content category; `sample_rows_sent` |
| `provenance` | metrics/figures/tables in the report; share with a complete artefact → step → script → run chain (`coverage`) |
| `results` | primary metric on validation and test (name, value, CI if recorded), selected model |
| `safeguards` | count of each engine refusal (scope, static, fit, test lock, gate, privacy), with step IDs |
| `decisions` | ordered list of `(event, action_id, params-hash, principal)`, used for consistency across runs |

- **Test:** golden synthetic run (driver mode, fake provider) → a metrics file with the expected counts. Brain-mode MCP run → `models.external_agent` is `unavailable`, not zero.

#### P10.5 Import client-reported usage for brain mode (R1-4, minimal tracking)
`mlca usage import --client claude|codex --session PATH_OR_ID [--from TS --to TS]` reads the agent client's own local transcript after a run. It takes only the usage numbers (model, input, output and cache tokens, timestamps) for messages within the project's run window, and writes them to `usage.jsonl` with `role: external_agent`, `cost_source: client_reported`.
- **Claude Code:** session JSONL under `~/.claude/projects/<cwd-slug>/`. Each assistant message has `message.model` and `message.usage` (checked on this machine, Claude Code 2.1.292).
- **Codex:** session files under `~/.codex/sessions/`. Check the format against the installed version, and record it in `docs/metrics.md`.

Never copy message text, only the numbers. The import is idempotent (keyed by message or request id).

- **Test:** small fixture transcripts for both formats, plus a run-window filter test.

#### P10.6 `mlca bench` (independent end-to-end reruns, R1-2a)
- `mlca bench run TASK_CARD --runs N --out DIR [--mode driver] [--budget-usd X] [--seed S]`. It creates N fresh projects from the same data and brief and drives each one headless to `report` or failure.
- Each run is a **fresh end-to-end agent run with new model calls**. This is distinct from `mlca replay --verify`, which reruns frozen code; the metrics label which is which.
- **Task card** (`docs/task-cards/*.yaml`; this is also the reviewers' R1-3 material). It holds:
  - the data path and the brief answers;
  - the template;
  - the option policy: `navigator_first` (take the Navigator's first option), `default_first`, or `seeded_random`;
  - optional per-event custom instructions (verbatim text);
  - the approval policy: confirm sub-goals with a fixed note, unlock the test set once in `test`, package list allowed or denied;
  - per-run and total budget.

  The task card's sha256 goes into every run.
- Policy decisions are recorded with principal **`user:policy/<task-card-sha12>`**. They are never counted as human decisions; reports list them separately.
- Runs are sequential by default (`--parallel K` optional). A run stopped by budget or failure is still reported; failed runs are **kept**, never dropped.
- `mlca bench summarize DIR` writes `bench_summary.json` and `bench_summary.md`:
  - completion rate;
  - failures by category;
  - steps per run; first-try success rate; automatic recovery rate;
  - interventions (policy versus human);
  - time breakdown (mean ± SD);
  - tokens and cost (mean ± SD, with `cost_source`);
  - final validation/test metric (mean ± SD, min, max);
  - **decision consistency**: the share of runs with identical action sequences per event, and pairwise agreement of the `decisions` lists.
- Brain-mode bench (an external agent driving N runs) is out of scope. Brain-mode runs are measured one by one with `mlca metrics` plus P10.5.
- **Test:** `mlca bench run` on the synthetic task with the fake provider and N=3 → three completed runs and a summary with the expected values; a forced failure in one run → completion rate 2/3, and the failed run is still listed.

#### P10.7 Documentation
- `docs/metrics.md`: every field, its source and its limits. Covers what `human_active_s` means; why brain-mode tokens are client-reported; `replay --verify` versus `bench`; and that the policy principal is not a human.
- One paragraph in the README.
- Link from `docs/m7-vm-brain-mode.md`: after the VM run, also run `mlca metrics` and `mlca usage import --client claude`.

**Done when:**
- every P10 test passes, and the full suite stays green;
- `mlca metrics` on the reviewer's synthetic MCP brain run and on a driver-mode run shows plausible, sourced values;
- `mlca bench run` with the fake provider and N=3, then `summarize`, works end to end;
- `docs/metrics.md` is written;
- local commits per sub-phase (`P10.<n>: …`); nothing published.

---

## 9. Borrowed material: exact sources and actions

> **Status:** ✅ All rows were reimplemented or used as reference; nothing was copied (`THIRD_PARTY_NOTICES.md`). The opencode logo files were **not** copied: the banner is original, generated from the author's logo (`scripts/make_logo.py`).

| What | Source (read-only) | Action | Destination |
|---|---|---|---|
| Process-group kill on timeout, env scrubbing, output caps, framed result protocol | Hermes `tools/code_kernel.py` (docstring lines 1–16; `_spawn` ~line 611, `start_new_session=True`; `_await_cell` ~line 760), `tools/code_execution_env.py` | **reimplement** (no copy; the files import 8–12 Hermes modules) | `runner/process.py` |
| Cell result shape (`status`, `stdout`, `stderr`, `*_clipped`, `traceback`) | Hermes `tools/code_kernel.py` `RUNNER_CELL_SOURCE` (~lines 47–74) | **reimplement** as the `RunFinished` payload | `log/schema.py` |
| Question/answer shape: options with label + description; answer `{selected[], custom?}` | deepseek `packages/interaction/user-questions/src/types.ts` (lines 10–70) | **adopt the schema** in Python | `engine/options.py`, `api.py` |
| Goal continuation in rounds (keep going while a goal is active, each round logged) | deepseek `packages/goal/goal-round-driver/src/index.ts`, `prompt.ts`; `docs/subsystems/goal.md` | **reimplement the idea**: our goals are fixed per event, sub-goals checked by code | `engine/turn.py` |
| Plan-before-execute, ask-user and permission patterns | opencode `packages/opencode/src/tool/question.ts`, `tool/plan.ts`, `permission/` | **reference only** | — |
| Main vs auxiliary model per task | Hermes `cli-config.yaml.example` ("Auxiliary Models" section, ~line 860), `agent/auxiliary_client.py` | **reference only** → our `roles:` config | `config.py` |
| Python core ↔ TS TUI/desktop split | Hermes `tui_gateway/`, `ui-tui/`, `apps/desktop/` | **architecture reference** (P9) | `clients/` |
| Terminal block-letter logo rendering | opencode `packages/tui/src/logo.ts` (11 lines), `packages/tui/src/component/logo.tsx` (61 lines), MIT | **copy** in P9 only, with attribution; P7 uses an original `assets/banner.txt` | `clients/tui-ink/` |
| ML project structure: numbered scripts, configs, run ledger, locked study definition | pelliscope-train `scripts/` (01_…61_), `configs/`, `coordination/RUN_LEDGER.csv`, `docs/STUDY_LOCK.md` | **pattern**: numbered materialised scripts; usage/run ledger fields; split lock. Do not copy code | `project/files.py`, `engine/split.py` |
| v1 event names and parameterised prompts | `ml-copilot-agent/ml_copilot_agent/workflow.py` (`master`), `git show origin/v1.5:ml_copilot_agent/workflow.py` | **lineage only** (docs/lineage.md). Do not reuse prompts | `docs/lineage.md` |
| v1 logo | `ml-copilot-agent/ml-copilot-agent.png` | only if D5 = yes; convert to black-and-white | `assets/logo.png` |

For every **copy**, add a row to `THIRD_PARTY_NOTICES.md` (source repo, commit, path, licence, what changed) and keep the original licence header.

---

## 10. Coding standards

- Python ≥ 3.11, type hints everywhere, `ruff` (line length 110), no global mutable state except the registry caches.
- Pure functions for replay, gates and checks (state in, result out); filesystem access only in `store`, `runner`, `project`, `report`.
- Prompts live in `roles/prompts/*.md` with `{placeholders}`, never as inline strings in Python. Each prompt file starts with a comment listing its placeholders and the response schema.
- Every user-visible string in the CLI and TUI comes from one module (`mlca/ui_text.py`), so wording can be revised in one place.
- Errors: user errors raise `MlcaUserError` (shown cleanly); internal errors keep tracebacks and are written to `.mlca/log/errors.log`.

---

## 11. Test data and the golden run

> **Status:** 🟡 Replaced for now by synthetic fixtures (`tests/fixtures/make_synthetic.py`, `synthetic_brief.yaml`, `synthetic_fake_llm.yaml`) driving the full path in `tests/integration/test_default_path.py`. ⬜ The anemia golden run is not written yet; the author will supply the data location.

- Unit fixtures are synthetic and committed (`tests/fixtures/tiny_tabular.csv`, about 200 rows, generated by `tests/fixtures/make_fixtures.py` with a fixed seed).
- **Golden run** (`tests/integration/test_golden_anemia.py`):
  - data are read from `/home/prime/Documents/github/mlca-paper-codebases/mlca_experiments/final results/hfr/Anemia/anemia.csv` (1,421 rows; columns `Gender, Hemoglobin, MCH, MCHC, MCV, Result`);
  - the test **copies** it into a temp project folder and never writes to the original;
  - if the file is absent, the test is skipped with a message;
  - the fake provider script `tests/fixtures/fake_llm/anemia_run.yaml` drives one path through all events (choose option 1 in each turn, one custom instruction accepted, one rejected by layer 1, one Worker repair, a test unlock, final report).
- **Assertions:**
  - the log verifies;
  - replay equals the cached state;
  - every sub-goal is satisfied by a check;
  - the vault was not readable before unlock (level recorded);
  - every metric/figure has provenance;
  - the usage report matches `usage.jsonl`;
  - `mlca replay --verify` reproduces the outputs.
- This is a **harness test**, not a scientific result. Never report its numbers anywhere.

---

## 12. Open decisions for the author (record answers in `docs/DECISIONS.md`)

| ID | Decision | Default until decided | Status (2026-10-07) |
|---|---|---|---|
| D1 | Licence of MLCA v2 (v1 was CC-BY-NC-ND-4.0, unusual for code; MIT/Apache-2.0 are common for tools) | CC-BY-NC-ND-4.0 | ✅ resolved by the author for 0.2.0b1; official legal code in `LICENSE`, SPDX Python/npm metadata |
| D2 | Content of the `tabular_classification` template: event goals, sub-goals, actions, prompts, scope text | agent writes short DRAFT content | 🟡 v0.2.0 content written with the author's direction (2026-10-06); defaults await author review |
| D3 | PyPI/npm package name | `mlca` | 🟡 author-approved `mlca`, but PyPI rejected it as too similar to another project; replacement name or registry resolution required. npm publishing remains unauthorized |
| D4 | Default models per role | none; onboarding asks | ⬜ open |
| D5 | Reuse v1 logo (black-and-white) or design a new one | original text banner only | ✅ resolved: the author's logo → `assets/logo_source.png`, `assets/logo.txt`, `assets/logo.png` |
| D6 | GitHub: new repository or v2 branch of `VatsalPatel18/ml-copilot-agent` (tag v1 `v0.1.9-legacy`) | local repository only, no remote | ⬜ open; no remote (needed before CI and releases run) |
| D7 | ChatGPT-account login and opencode free models, after a terms check (7.6.6) | not implemented | ⬜ open; not implemented |
| D8 | Second template: survival (default) or subtyping/clustering | survival | ✅ survival (`templates/survival/`), content DRAFT |

---

## 13. Evaluation checklist (used to review the finished work)

> **Review 2026-10-06 (`61cb041`):**
> 1. ✅ All eleven invariants have offline regression coverage after MCP M0; native/live validation remains pending.
> 2. ✅ 54 passed / 1 skipped, ruff clean, `replay --verify` reproduces. Offline tests need a primed uv cache.
> 3. ✅ No model names or keys in `src/`.
> 4. 🟡 Mechanisms present; only some are proven by tests.
> 5. ⬜ Untested.
> 6. ✅ Level A verified by test and manual probe; level-B limits documented in `docs/security-model.md`.
> 7. ✅ Line counts match; the sample-row guard is untested.
> 8. ✅ Reports regenerate from the log alone.
> 9. ✅ Freeze, edit detection and read-only permission regression are covered after MCP M0.
> 10. ✅ No remote, nothing published.
> 11. ✅ Nothing copied.
> 12. ✅ `docs/DECISIONS.md` maintained.

1. Every invariant I1–I11 has code at the named location and at least one test that fails if the code is removed.
2. `uv run pytest` passes offline; `ruff check` is clean; the golden run passes; `mlca replay --verify` reproduces.
3. No model name, API key, absolute user path (other than the golden-run data path in the test) or secret is hard-coded in `src/`.
4. Navigator output can never: add an action outside the catalog, mark a sub-goal done, add the custom option, or unlock the test partition (tests prove each).
5. A layer-1 scope rejection makes zero model calls.
6. Under level A, a generated script cannot read the vault, the key or the original data after the split; level B limits are documented honestly.
7. Every model request has exactly one usage line and one egress line; `sample_rows` never leaves the machine unless enabled.
8. Reports regenerate from the log and step folders alone, with no model calls.
9. Step folders are immutable; materialised views detect user edits.
10. Nothing outside this repository was modified; no remote added; nothing published.
11. `THIRD_PARTY_NOTICES.md` lists every copied file; nothing was copied that section 9 marks reimplement/reference.
12. `docs/DECISIONS.md` records each deviation from this plan, with its reason.
