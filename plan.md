# MLCA v2: implementation plan

## Current P17/P18 status — 14 October 2026

**Author decision (2026-10-14): the no-AI reference arm is dropped from all bench and bio-bench comparisons.** Only real model runs are measured (driver and brain arms). The reference code stays in the repository unused; the seven offline reference attempts of 14 October are development tests, not experiments.

WP1–WP7 completed locally. Final suite: **296 passed, 1 skipped**; experiments tests: **7 passed**.
Seven offline reference attempts recorded zero model requests: S1 core complete with four custom
instructions not achieved; S2 has four interpretation timeouts and two HER2 bootstrap NaN errors.
Exports pass hash/exclusion auditing. Full protocols are not claimed successful. No live calls,
freeze, push, upload, publishing or paper edit. See docs/IMPLEMENTATION_STATUS.md and the
experiments `bio-bench/acceptance/2026-10-14/` summary. Earlier dated entries are historical.

## Beta 2 published and beta 1 yanked — 2026-10-13

Published [mlcagent 0.2.0b2](https://pypi.org/project/mlcagent/0.2.0b2/) using the authorized upload token; both public artifact hashes match. Fresh isolated HOME/XDG PyPI install, version, doctor and 14-tool MCP verification pass. Beta 1 is yanked (both files), verified in release management and public PyPI JSON. Local tag v0.2.0b2 records release source bdc2f376ef2b9b2848d5f5ed5b272ee9aad2a311; global mlca was refreshed to 0.2.0b2. No GitHub/npm push or publication occurred. Master and uncommitted browser plans remain untouched.

Final suite: 193 passed, 1 skipped in 647.09 s; lint/format, metadata, wrappers, Twine, wheel resources and isolated synthetic init/permission-preview pass. Real OAuth/model/data validation and OpenAI registration remain pending. The token was read only by the publish command and never displayed, copied or committed.


Plan for a coding agent. It specifies a new harness, **MLCA v2** (ML Copilot Agent, revised), to be built in this repository: `/home/prime/Documents/github/mlca-paper-codebases/mlca-revized/`.

Written 2026-10-06. When the code is done, it will be reviewed against section 13 (evaluation checklist). Read the whole file before writing code. Where this plan and the code you find disagree, stop and record the conflict in `docs/DECISIONS.md`. Do not guess.

---

## Revision cut implemented — 2026-10-13

P16.1–P16.4 plus metadata backfill and P14.6 template-option recovery are implemented.
Full offline working-tree suite: **245 passed, 1 skipped in 678.51 s** (PowerShell unavailable). Ruff lint and formatting pass. The isolated selective P16/P14.6 candidate passed 34 tests, independently of the other uncommitted work.
Pending: Activity reconciliation (real CSV required), explicitly authorized live smoke, and post-freeze P14/P15 product work. No publishing, push, tag, version bump or installed-tool refresh. Other uncommitted changes are preserved.

## Earlier beta-2 status — 2026-10-13

P11.1–P11.7 implemented on native-onboarding, master untouched. Full offline suite: **193 passed, 1 skipped in 647.09 s** (PowerShell unavailable). Ruff lint/format, release metadata and wrapper checks pass. Rebuilt wheel/sdist pass Twine and the 206-entry wheel check. Isolated HOME/XDG install, version/doctor, synthetic initialization and 14-tool MCP discovery pass; Claude registration/skill preview writes no configuration. No live models, real OAuth authorization or original-data study was run.

Beta 2 (mlcagent 0.2.0b2) publication and subsequent beta 1 yank are author-authorized. Final upload and public verification follow; no GitHub/npm publication.

## Prior release status — 2026-10-07

**Published beta:** [`mlcagent` 0.2.0b1](https://pypi.org/project/mlcagent/0.2.0b1/). Both files were accepted by PyPI with the author-provided token; public SHA256 hashes match the tested artifacts. Local release source: `16bcc72`.


**Latest work:** P10.1–P10.7 implemented with sourced metrics, usage imports and independent task-card benchmarks. The author-approved distribution is `mlcagent` 0.2.0b1; command/import remain `mlca`. Release validation passed (137 tests passed, 1 skipped). Both artifacts are published at [https://pypi.org/project/mlcagent/0.2.0b1/](https://pypi.org/project/mlcagent/0.2.0b1/); fresh-index installation and 14-tool verification passed. Older upload results below describe the rejected `mlca` name, not this release.


### Historical beta publication attempt as `mlca` — 2026-10-07

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
- **P10 evaluation instrumentation:** implemented in local sub-phase commits (section 8, P10); targeted tests pass. Full release-suite validation passed: 137 passed, 1 skipped. Original-data and live-provider measurements remain pending.
- **P11 guided TUI and provider switching** (implemented 2026-10-13; live authorization pending): option cards, engine-appended human-decision cards, visible agent progress, left-to-right journey strip, model status and switching at any time, OpenAI sign-in through the official program (section 8, P11).
- **P12 no dead ends + AI-assisted setup + card design** (planned 2026-10-13, from the second hands-on run): visible model connection, refusal reasons on screen, missing fields named, target recommendations (model or rules), readable cards, "Project setup" naming (section 8, P12).
- **Browser edition (driver mode in WebAssembly):** planned separately in [`plan_web.md`](plan_web.md) (2026-10-12); branch `web-edition`, after the paper's code freeze. Brain mode stays native; its browser follow-up `mlcagent-web-mcp` is mapped in [`plan_web_mcp.md`](plan_web_mcp.md).
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
- `npx mlcagent` launcher: an npm package that installs/updates the Python core with uv and starts it (reference: Hermes `apps/bootstrap-installer/`, deepseek `npx @deepseek-ai/dsh`).
- Illustrator role (image generation via OpenRouter image models), only for diagrams and graphical abstracts, with outputs in `reports/illustrations/`, never as analysis artefacts.
- ChatGPT-account login and free models (7.6.6), only after the terms check.
- Web client hosted on Firebase (static), only as a front end to a locally running core.

### P10: evaluation instrumentation (metrics for the paper; do before the author's first VM test)

> **Status:** ✅ P10.1–P10.7 implemented in local sub-phase commits. Full beta release-suite validation passed: 137 passed, 1 skipped. M7 remains an author-run client/provider test.

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

> **Status:** ✅ implemented; details and validation in `docs/IMPLEMENTATION_STATUS.md`.
- Write timing into the existing decision records:
  - **`OptionChosen` and `CustomInstructionSubmitted`:** `decision_wait_s` (seconds since the matching `OptionsProposed`), and `principal` (already present).
  - **`CustomInstructionSubmitted`:** `chars` and `words` of the instruction.
  - **`ApprovalResolved`:** `wait_s` (since `ApprovalRequested`). For `UserConfirmed` without a request, `wait_s` runs from when the sub-goal first became the only open one.
  - **TUI only:** `active_s`, the time with keyboard or mouse activity while that decision was pending. A gap longer than 120 s counts as idle and is excluded; the cutoff is recorded with the value. CLI and MCP decisions have no `active_s` (`unavailable`); their `decision_wait_s` is an upper bound.
- `ScriptEditedByUser` gains `lines_changed`.
- **Test:** timings are present and non-negative; idle gaps are excluded in a Textual pilot test with simulated keystrokes and a fake clock.

#### P10.3 Failure categories (R2-2, R1-2a)

> **Status:** ✅ implemented; details and validation in `docs/IMPLEMENTATION_STATUS.md`.
Every refusal or failure record gets a `category` from a fixed list, set where it is written (not guessed later):
`static_check`, `sandbox_denied`, `runtime_error:<ExceptionType>`, `timeout`, `missing_output`, `fit_rule`, `test_lock`, `scope_layer1`, `scope_layer2`, `gate_blocked`, `invalid_options`, `provider_error`, `budget_stop`, `privacy_refusal`, `abandoned`.

- **Test:** one case per category.

#### P10.4 `mlca metrics` (single project, any mode)

> **Status:** ✅ implemented; details and validation in `docs/IMPLEMENTATION_STATUS.md`.
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

> **Status:** ✅ implemented; details and validation in `docs/IMPLEMENTATION_STATUS.md`.
`mlca usage import --client claude|codex --session PATH_OR_ID [--from TS --to TS]` reads the agent client's own local transcript after a run. It takes only the usage numbers (model, input, output and cache tokens, timestamps) for messages within the project's run window, and writes them to `usage.jsonl` with `role: external_agent`, `cost_source: client_reported`.
- **Claude Code:** session JSONL under `~/.claude/projects/<cwd-slug>/`. Each assistant message has `message.model` and `message.usage` (checked on this machine, Claude Code 2.1.292).
- **Codex:** session files under `~/.codex/sessions/`. Check the format against the installed version, and record it in `docs/metrics.md`.

Never copy message text, only the numbers. The import is idempotent (keyed by message or request id).

- **Test:** small fixture transcripts for both formats, plus a run-window filter test.

#### P10.6 `mlca bench` (independent end-to-end reruns, R1-2a)

> **Status:** ✅ implemented; details and validation in `docs/IMPLEMENTATION_STATUS.md`.
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

> **Status:** ✅ implemented; details and validation in `docs/IMPLEMENTATION_STATUS.md`.
- `docs/metrics.md`: every field, its source and its limits. Covers what `human_active_s` means; why brain-mode tokens are client-reported; `replay --verify` versus `bench`; and that the policy principal is not a human.
- One paragraph in the README.
- Link from `docs/m7-vm-brain-mode.md`: after the VM run, also run `mlca metrics` and `mlca usage import --client claude`.

**Done when:**
- every P10 test passes, and the full suite stays green;
- `mlca metrics` on the reviewer's synthetic MCP brain run and on a driver-mode run shows plausible, sourced values;
- `mlca bench run` with the fake provider and N=3, then `summarize`, works end to end;
- `docs/metrics.md` is written;
- local commits per sub-phase (`P10.<n>: …`); nothing published.

### P11: a TUI that guides, plus providers you can switch at any time

> **Status:** ✅ P11.1–P11.7 implemented on native-onboarding; full suite passes (193 passed, 1 skipped), with final release validation recorded. OpenAI sign-in remains registration-gated; real-provider and native keyring checks are pending. Details: docs/IMPLEMENTATION_STATUS.md.
> Engine guidance is opt-in for TUI presentation, preserving existing MCP/CLI action IDs; account quotas stay unknown unless explicitly reported. Cancellation during execution remains the engine timeout/budget boundary.

**What went wrong in that run:**
- the options were not recognisable as distinct choices;
- after the only scripted action in `onboard`, the screen said "All available actions are exhausted". The remaining steps (choose the target column, confirm the brief, move on) were hidden behind footer hotkeys (`d`, `f`, `n`);
- the orange panel showed raw engine records (`TurnStarted`, `SubgoalChecked …`);
- nothing showed whether the model was connected or which one answered.

**Goal:** at every moment the screen says, in plain words, **where you are, what just happened, and your 2–4 choices**, while the agent works visibly in the background.

**Rule kept from §3:** human and navigation cards are appended **by the engine**, never by the Navigator (I5, I6). The Navigator still proposes only catalog actions.

#### P11.1 Options as cards
- **One card per option**, numbered and keyboard-selectable (`1`–`n`, arrows + Enter):
  - title (≤ 8 words);
  - one line on what it does;
  - "produces: …" (the action's outputs);
  - "why now: …" (the sub-goal or fact it advances);
  - a source tag (`agent` / `template` / `you decide`);
  - estimated cost or time where known.
- **Human-decision cards as numbered cards**, appended by the engine whenever a sub-goal needs a person or the event is done:
  - "Choose the target column" (opens Study details);
  - "Confirm the study brief" (the confirmation dialog with a note);
  - "Continue to <next event> →";
  - "Return to <event>" (validation loops);
  - "Custom instruction" is always the last card.

  The footer lists only the keys of the cards shown.
- **Never show "All available actions are exhausted".** Instead, a plain sentence plus the human cards, e.g. "Inventory recorded. Next, choose what to predict."
- Files: `tui/widgets/options.py` (card widget), `api.py: options()` (engine-appended human cards with their action), `ui_text.py`.

#### P11.2 Visible agent work
- **While the Navigator prepares options:** an animated card, "Agent is preparing options…", with the model name and elapsed seconds.
- **While a step runs:** a progress card with phases that tick:
  1. writing the script;
  2. checks;
  3. running in the sandbox (attempt n/3);
  4. collecting outputs;
  5. checking sub-goals.

  On failure: the reason in one plain line, then the repair attempt.
- Use Textual's spinner or `LoadingIndicator`; the UI never blocks; `Esc` cancels where the engine allows it.
- Files: `tui/app.py` (worker callbacks), `tui/widgets/progress.py` (new).

#### P11.3 The journey panel (replaces the raw orange log)
The bottom panel, top to bottom:
1. **Event strip, left to right with arrows:** `onboard ✓ → data ● → eda · → split 🔒 → preprocess · → …`. Done ✓, current ●, locked 🔒; it updates live.
2. **Action trail** for the current branch, left to right: `Record brief ✓ → Choose target ✓ → Audit schema ✓ → Count classes ⏳`. Human decisions are included and marked as yours; it scrolls when long.
3. **Plain-English log**, generated from records through one message map in `ui_text.py`:
   - "✓ Registered table breast_cancer_diagnostic_uci (569 rows, 31 columns)";
   - "⚠ Target column not chosen yet: card 1";
   - "✓ Brief recorded".

   The raw engine log moves to a toggle (`L` "engine log") for debugging.

Files: `tui/widgets/log_stream.py` → `tui/widgets/journey.py`; `event_graph.py` can shrink to the left list or merge into the strip.

#### P11.4 Model status, and switching provider or model at any time
- **Status line:** `● OpenRouter · openrouter/free → last answered by <model_reported> · 12/50 today`. The dot is green (last call OK), yellow (rate-limited or slow), red (failing), or grey ("not connected: press m"). Plus a per-role summary (Navigator, Worker).
- **Test connection:** one small call per role, showing OK, latency and the model that answered. It counts as a request, so the button says so.
- **`m` opens the Models panel.** Per role: choose a provider and model, and sign in or out. The providers:
  - OpenRouter sign-in (exists);
  - OpenAI sign-in (P11.5);
  - OpenAI API key;
  - local Ollama (auto-detect `localhost:11434`);
  - custom OpenAI-compatible.
- **A change takes effect at the next model request,** never in the middle of a step. It writes a new record `ModelChanged {role, from, to, provider, principal, reason}`.
- **Reports and metrics** show which model answered each step (already in `model_reported`) and every switch. `mlca bench --lock-models` forbids switching during measured runs.
- **`mlca auth status`** lists signed-in providers, never values. All credentials live in the keyring, one entry per provider.
- Files: `tui/screens/model_picker.py`, `tui/widgets/status_bar.py`, `config.py`, `llm/client.py`, `llm/credentials.py`, `log/schema.py` (record type), `evaluation/metrics.py`.

#### P11.5 OpenAI sign-in ("Sign in with ChatGPT")
- **Use OpenAI's official "Sign in with ChatGPT" program for third-party apps** (launched late September 2026; open-source apps self-serve, commercial apps apply).
  - The author registers MLCA and gets **MLCA's own client ID**, kept in config.
  - **Do not reuse the Codex CLI client ID or private ChatGPT backend endpoints** shown in third-party snippets.
  - Take the endpoints, scopes and the plan-usage approval step from OpenAI's current developer docs at implementation time, and record them in `docs/providers.md`.
- **Flow:**
  - browser PKCE with a localhost callback, or device code / pasted redirect URL on SSH;
  - access and refresh tokens in the keyring, refreshed automatically;
  - the user's approval for MLCA to use their plan allowance (with its cap) as the program requires;
  - a new provider kind `openai_chatgpt` on the API surface the program documents.
- **Until registration exists:** show "Sign in with ChatGPT" disabled with a one-line reason; the OpenAI API key path (keyring) works meanwhile.
- Files: `llm/openai_auth.py` (new, mirrors `openrouter_auth.py`), `llm/providers/openai_chatgpt.py`, `tui/screens/openai_signin.py`, `cli/main.py` (`mlca signin --provider openai`).

#### P11.6 Existing folders and failed initialisation
- Verify commit `245ac50` ("offer a fresh study after existing-folder refusal"). Opening a folder that holds a study offers **Open** or **New study** (a new subfolder, `study-002`, …), never overwriting.
- **Make initialisation atomic:** build in a temporary folder and rename it at the end. A failed init then leaves no half-made `.mlca/`. An old partial folder is detected and offered for cleanup, with a confirmation.

#### P11.7 Tests and docs
- **Textual pilot tests:**
  - cards render, and keys map to visible cards;
  - human cards appear when only human sub-goals remain;
  - "exhausted" never appears;
  - the progress card ticks through its phases (fake provider, fake clock);
  - the journey strip and trail update after each step;
  - `m` switches the model and writes `ModelChanged`;
  - the status dot changes on fake success, rate-limit and failure.
- **Auth tests:** OpenAI sign-in with mocked endpoints and a mocked keyring; no live calls.
- **Docs:** README screenshots; `docs/providers.md` (switching, sign-ins, free tier); the first-run part of `docs/m7-vm-brain-mode.md`.

**Done when:** a new user can init a study, see 2–4 clear cards, follow the journey strip, see which model is connected, switch provider mid-study, and reach `data` without knowing any footer hotkey. All tests green; local commits `P11.<n>: …`; nothing published.

### P12: no dead ends, AI-assisted project setup, and a readable card design

> **Status:** ⬜ planned 2026-10-13, from the author's second hands-on run (`benchmark_datasets/study-002`, dry bean data, 0.2.0b2).

**What the event log of that run shows** (the engine worked; the screen hid it):

| Seen by the author | What actually happened (log) |
|---|---|
| No idea which model or provider is connected | **None is.** No `~/.config/mlca/config.yaml`, no roles, project config `{}`; status `requests 0`. Every card came from the template; no AI ran at all. Nothing on screen said so |
| "Submit" in Custom instruction does nothing | Both instructions ("Execute and train whatever model you like…") were **rejected by scope layer 1** in `onboard` (`ScopeDecision reject: Instruction conflicts with the current event scope`). The reason was never shown. Without a Worker model, an accepted instruction would also have failed |
| Stuck in a loop on "Complete the study details" | Study details were saved with the target `Extent` but **without "what one row represents"**. `study_ready` stays false ("Explain what one row represents…"). That message existed only in the log; meanwhile the scripted card "Record brief and data inventory" was hidden, and `next` said only "gate blocked" |
| No help choosing the target | The dialog says "no automatic target selection". `Extent` (a numeric feature) was chosen; the dataset's real outcome is `Class` (7 categories) |

#### P12.1 Always say what is connected, and what that means
- **First screen, and the status line**, when no model is configured: `○ No AI model connected: cards come from the built-in workflow, custom instructions and scripted steps cannot run. Press m to connect (free with OpenRouter).` Make it a **card** too ("Connect an AI model"), not only a footer hint.
- **When connected:** `● OpenRouter · Navigator: openrouter/free · Worker: openrouter/free · last answer: <model> · 3/50 today`. Show it in the header of the main screen, not only the status bar.
- **A session-only key** (no keyring) says so: "signed in for this session only".
- **Driver-mode actions that need a model** (a scripted step, custom instruction, AI suggestions) show **"needs an AI model"** on their card and open Models when chosen without one.
- **Brain mode:** "Driven by <agent>" (MX3) instead.

#### P12.2 Never fail silently
- **Every refusal is shown where the user acted,** in plain words with the way forward, inside the dialog or as a sticky banner (not a toast that vanishes):
  - layer-1 scope: "This belongs to a later step: model training starts in **Model**. Here you can ask about the brief and the files";
  - layer-2 scope;
  - gate: "Can't continue yet: still missing **what one row represents**";
  - static checks, budget, provider errors.
- **The Custom instruction dialog** shows the current event's scope above the text box ("In Project setup you can: …") and keeps the text after a rejection.
- **Test:** a pilot test submits an out-of-scope instruction, and the reason is visible on screen.

#### P12.3 No dead ends in Project setup
- **The study details dialog validates on Save.** Missing required fields are highlighted inline ("Required: what one row represents"). Saving a partial draft is allowed, but the card then names what is missing: "Complete the study details: still missing *row meaning*".
- **Show the path, even before it is open:** "Record brief and data inventory" stays visible, disabled, with "available after study details".
- **Plain-language sub-goals:**
  - human text without ids;
  - coloured state: ✓ green done, ● yellow current or pending, ✗ red failed;
  - the *detail* of a failing check shown under the line ("Explain what one row represents").
- **A "Next:" line** in the activity panel, always generated from the first unmet sub-goal: "Next: tell MLCA what one row represents (card 1)".
- **Test:** saving without the row meaning leads to the card naming it; after it's filled, the scripted card becomes active; no state exists where no enabled card advances an unmet sub-goal.

#### P12.4 AI-assisted study setup (suggests; you decide)
- **New Navigator purpose `suggest_study_fields`**, run once after registration and again on request ("Suggest again").
  - **Input:** the inventory summary (column names, types, unique counts, missing share; example values only if `allow_sample_rows`) and the aim.
  - **Output** (structured, validated against the real columns):
    - ranked target candidates with reasons;
    - task type (binary, multiclass, regression, survival with duration and event);
    - a suggested row meaning;
    - repeated-subjects guess;
    - an aim draft.
- **Built-in rules** when no model is connected, in brain mode, or when the quota is out (labelled "suggested by rules"). Score by:
  - outcome-like names (`class`, `label`, `target`, `outcome`, `diagnosis`, `result`, `status`, `y`, `event`, `death`, `survival`, `time`);
  - 2–20 distinct values for classification;
  - last column;
  - not ID-like (unique ratio near 1, or names like `id`);
  - not a high-cardinality continuous measurement.

  For dry bean this ranks `Class` first.
- **The dialog:**
  - the dropdown opens with **"★ Recommended: Class: 7 categories · named like an outcome · last column"** at the top, then the other candidates with their reason, then all columns;
  - aim and row meaning are pre-filled as editable suggestions (e.g. "one bean, measured from an image");
  - the header changes to "MLCA suggests, you decide";
  - "I'll decide later" stays.
- **Saving is still the human decision** (`StudyFieldsResolved`, actor user), now with `suggested_by` (model id or `rules`) and `accepted | changed` per field, counted in metrics.
- **MCP:** `mlca_status` adds `study_suggestions_data` (the rules version), so a brain-mode agent can base its `study_fields` proposal on it.
- **Tests:** the rules rank `Class` first on `dry_bean_uci.csv` and the outcome first on the other benchmark tables; model suggestions validated, with an invalid column dropped; `suggested_by` and `accepted` recorded.

#### P12.5 A card design that reads at a glance
A terminal cannot change font size per widget. Clarity comes from layout, weight, colour and space:
- **Left-aligned cards** (the current text is centred), in a two-column grid when the window is wide.
- Each card has:
  - a **large number badge** (3-line block digit), and the title in **bold bright** text, ≤ 6 words;
  - one plain sentence of what happens;
  - **"• Produces:" bullets** listing the outputs (e.g. "• inventory of 1 table · 13,611 rows", "• brief.json");
  - a small origin mark only: ✦ for AI-suggested, with the model name on focus; nothing for built-in steps; and **no "you decide" label**.
- **States:** focused = bright border and lifted background; disabled = dim with its reason; needs model = amber mark.
- **The colour system,** used everywhere (cards, sub-goals, journey strip, left event list): green done, yellow current, red error, grey locked or ahead.
- **Spacing:** one blank line between title and bullets, and between cards; the activity panel kept to 5 lines, with a "More" toggle.
- **Larger fonts** exist in the browser edition (`plan_web.md`). Until then, `mlca web` lets the browser zoom the same TUI.
- **Test:** Textual snapshot tests of the main screen in four states (no model; setup missing a field; ready; step running).

#### P12.6 Names
- Event `onboard` displays as **"Project setup"** in both templates. The event id stays `onboard`, so logs and reports stay compatible; bump the template version (0.2.1). Existing studies keep their snapshot.
- **"Onboarding"** now means only the first-run configuration: models, OpenRouter/OpenAI sign-in, sandbox check. Rename the welcome flow's "Configure models" accordingly.

**Done when:** on `dry_bean_uci.csv` with no model connected, a new user:
- sees "No AI model connected" and can connect from a card;
- sees `Class` recommended;
- is told exactly which field is missing;
- sees every refusal reason on screen;
- reaches `data` without help.

With OpenRouter connected, the status names the model that answered. All tests green; local commits `P12.<n>: …`; nothing published.

#### P12.7 Models panel: easy to find, one action to connect, minimal text
**Found in the author's run (2026-10-13 08:00):**
- the panel was hard to find (only `m` in the footer);
- OpenRouter browser sign-in **succeeded** ("Authorization received"; the panel showed "OpenRouter connected");
- but afterwards **nothing was persisted**: no `~/.config/mlca/config.yaml`, no roles, and `mlca auth status` → `{}`. The Navigator and Worker stayed unset until a Save button below the fold was pressed;
- the panel shows about 15 controls and long explanatory lines at once.

**Changes:**
- **Finding it:** the "Connect an AI model" card (P12.1); the model status in the header opens Models on Enter or click. On first launch with no model configured, Models opens automatically once.
- **One action connects:** a successful "Start free with OpenRouter" immediately does three things:
  1. stores the key (keyring, or the session with a visible "this session only" note);
  2. **saves** the Navigator and Worker as `openrouter/free` in the user config;
  3. returns to the main screen with `● Connected: OpenRouter · openrouter/free`.

  No separate Save step. The same goes for a pasted OpenAI key or a detected local Ollama: choose it → connected → saved.
- **Layout: the first view has only:**
  - the connection status line;
  - three large buttons: **Start free with OpenRouter** · **Use an OpenAI API key** · **Use a local model**;
  - one dim line: "Sign in with ChatGPT: coming soon";
  - **Change model** (opens the model browser).

  Everything else sits under a collapsed **Advanced**: separate Worker model, environment variable name, endpoint URL, keyring toggle, sign-out buttons.
- **Text rule (applies to all MLCA screens and dialogs):**
  - one short label per control (≤ 6 words);
  - at most one helper line per section (≤ 12 words);
  - longer explanations behind a `?` toggle or in `docs/`;
  - no implementation terms on screen (e.g. "environment variable", "session keys", "secure OS keyring" become "Advanced").

  The same rule holds for the AI role prompts (`roles/prompts/*.md`): keep them minimal and directive. The shared Worker preamble and output contract stay; the event and action text stays in the templates.
- **Model browser, found empty in the same run.**
  - **Cause:** the picker shows only the cached catalogue, and on first use there is no cache. It also says "Cached catalogue may be stale" even when nothing is cached. A direct `catalog.fetch` against OpenRouter on 2026-10-13 returned 459 models, 19 free, including `openrouter/free`.
  - **Fix:**
    - **load the catalogue automatically** when the picker opens with no or stale cache (spinner "Loading models…");
    - on failure, show the error and keep manual ID entry;
    - say "No models loaded yet" rather than "stale" when the cache is empty;
    - pin **`openrouter/free` ("Free models router: picks a free model for each request")** at the top;
    - filter per role: the Navigator and Worker list only text-output models. The free list currently includes music and image models (e.g. `google/lyria-3-*`), which cannot write Python. Other models are shown dimmed with the reason.
- **Tests:**
  - picker opened with an empty cache → fetch runs (mocked) and the list fills, with `openrouter/free` first; non-text models are dimmed for Worker and Navigator;
  - a pilot sign-in with mocked OpenRouter endpoints → config written, roles set, main screen shows connected, no Save needed;
  - first launch without config → Models opens once;
  - snapshot of the simplified panel;
  - a lint test that fails when a TUI label exceeds the text rule (strings in `ui_text.py`).

### P13: the AI drafts, the author saves (2026-10-13 run, adult census)

What went wrong: the author did not know what one row represents; the confirm form asked for an internal sub-goal ID; "just complete the setup" was rejected as out of scope; the brief aim was the author's placeholder "Train AI model".

- **P13.1 AI-drafted brief.** The study dialog asks the Navigator for a draft (aim, target or duration/event, unit, repeated subjects) from the inventory summary (column names, types, counts; no rows). Fields fill as soon as it answers; without a model, the local rules fill the columns. The author edits or presses Save.
- **P13.2 One-click approval.** "Approve the brief" shows the recorded brief; no sub-goal IDs, note optional (default "Approved as shown").
- **P13.3 "Do it for me" works.** Instructions like "complete the setup" or "continue" open or run the first card instead of a scope rejection.
- **P13.4 Ready-made prompts.** The custom dialog always lists suggestions: "Complete this step for me" plus the step's actions; one click fills the instruction.
- **P13.5 Plain failures.** Show the actual reason, not "invalid options" or "runtime error: MlcaUserError".
- **P13.6 Card focus.** The focused card is outlined, not shown as reversed text blocks.
- **Tests:** draft parsing and fallback; approval without IDs; proceed intent; suggestion list; message wording.
- **Status (2026-10-13):** P13.1–P13.6 implemented, uncommitted in `native-onboarding`, installed as `mlca`. P13 is superseded in scope by P14.

### P14: autopilot for users who know no machine learning

**Target user.** A domain expert (clinician, biologist, analyst) who knows their data and question, but not machine learning. MLCA makes every technical decision with a stated, recommended default. It asks only questions the user can answer from domain knowledge, in plain words, each with a recommended answer. The study moves from event to event by itself.

**Revision cut (superseded 2026-10-13 by the author: build P14/P15 now; freeze after them).** The paper revision needs only the measurement path: `mlca bench` (driver) and one brain-mode run completing studies on real models, with pinned model IDs and a frozen version. Before the code freeze, only P14.6 (a weak Navigator never blocks) and fixes found by the smoke runs are in scope. P14.1 and P14.3–P14.5 are product work after submission. P14.2 interacts with what the paper evaluates (D14-1): for the measured runs the Worker writes the code, and its failures are results; reference scripts can only serve as a separate no-LLM baseline arm.

**Generic by construction.** Nothing may depend on a particular dataset, column name, class count or domain. Every rule below reads properties of the registered table (types, distinct values, missingness, relationships between columns) and the brief. The benchmark tables are acceptance inputs only, never sources of rules.

#### P14.0 Audit (2026-10-13): why the real run stopped

Evidence: the author's adult-census project log, the templates, the runner, and checks of the benchmark tables.

1. **The author's real run never left Project setup.**
   - Every Confirm failed, because the form required a typed internal sub-goal ID.
   - Both "do it for me" instructions were rejected by scope layer 2.
   - The Navigator option calls failed after setup (`runtime_error:MlcaUserError`): with only one human step left, the free model returned options the validator refused. The result was a silent fallback.
   - "I dont know honestly" was accepted as the unit of analysis.
2. **The main path depends on the Worker model writing Python.**
   - Only 3 of 20 actions are engine code: `inventory`, `split` and `report`.
   - The other 17, including schema audit, distributions, preprocessing, feature selection, training, scoring and interpretation, need an LLM to write correct code against `mlca_runtime` (`fit_record`, `record_metric`).
   - No full run from start to report has been done with a live model (M7 pending). The suite's scripted Worker responses prove the engine, not the product.
3. **Generic data situations no event handles.**
   - The same class spelled several ways.
   - More than two classes, while validation hard-codes binary ROC AUC and a Youden threshold.
   - A column that is a copy or a source of the outcome (leakage, the circularity the reviewers raised in R2-4/5).
   - Two outcome-like columns.
   - Identifier columns kept as features.
   - Duplicate rows.
   - Grouped rows (several rows per subject) without a group column.

   All four of the first situations occur in the benchmark tables.
4. **No way to ask.** The engine can only refuse. There is no mid-run question with a recommended answer.
5. **Human approvals use internal vocabulary:** sub-goal IDs, "custom scope" and "layer 2".

#### P14.1 Ask: interim questions (pattern from OpenCode's `question` tool)

Reference: `/home/prime/Documents/g3/support-git/opencode` @ `5a4dd5b430`, files `packages/core/src/tool/plugin/question.ts`, `packages/schema/src/question.ts` and `packages/tui/src/routes/session/form.tsx`. The pattern is reimplemented, not copied.

- **Record:** `QuestionAsked {question_id, event_id, asker: engine|navigator|worker, header ≤30 chars, question, options: [{label 1–5 words, description}], recommended: index, multiple, why}`, then `QuestionAnswered {question_id, answer, free_text, by: user|default}`. Both enter the event log, so reports cite every decision and who made it.
- **Display:**
  - The question docks in place of the status box, not as a pop-up.
  - ↑/↓ choose; the recommended option is first and marked "(Recommended)"; Enter answers.
  - The last row is always "Type your own answer".
  - Esc means "Use the recommended answer", recorded as `by: default`.
  - Several questions show as tabs (←/→) with a final Review tab.
- **Who asks:**
  - **Engine rules (P14.4):** deterministic triggers, no model needed.
  - **Navigator:** the options response may carry at most one `ask` instead of options when a choice needs domain knowledge. The engine validates it: options must be ≤4, and the answer must map to a parameter, a brief field or an action.
  - **Worker:** after a failed repair, it asks rather than failing silently, e.g. "Column X has text in a numeric field: treat as missing (Recommended) / drop rows / stop".
- **Answers act:** each option names its effect (set a brief field, set an action parameter, choose an action, or exclude a column). The engine applies it; free text goes to the Navigator for mapping, with a confirmation question.
- **Brain mode:** the MCP tools `mlca_questions` and `mlca_answer` expose the same records to the external agent. Human-only questions (P14.3 approvals) stay human-only.

#### P14.2 Built-in reference steps for the main path

Every event's **primary** action gets an engine-owned, parameterised reference script, run in the same sandbox and logged like any step. Parameters come from the brief, the answers and recorded facts; it is the same code for any table.

| Event | Primary action | Reference behaviour (generic) |
|---|---|---|
| Data | `audit_schema` | Per-column type, distinct values, missingness, identifier and constant flags; outcome coding (class counts, spelling variants) |
| Eda | `describe_distributions` | Numeric and categorical summaries, by outcome class when classes ≤ 20 |
| Split | `freeze_*` (engine, exists) | Method chosen by P14.4 rules: group if a group column exists, stratified when classes allow, random otherwise |
| Preprocess | `fit_preprocessing` | Impute, encode and scale by detected type; identifiers and excluded columns dropped; fit on train only |
| Features | `retain_features` / `select_features` | Keep all by default; filter only when features ≫ rows |
| Model | `train_logistic` (+ `train_alternative`) | Task-aware: binary, multiclass (multinomial) or survival (Cox), class-balanced |
| Validate | `score_validation` | Task-aware metrics: binary ROC AUC + threshold; multiclass macro one-vs-rest ROC AUC, no threshold; survival C-index |
| Test | `score_test` | The same metric set as validation, bootstrap CI, once |
| Interpret | `explain_model` | Permutation importance on validation rows |
| Report | `generate_reports` (engine, exists) | Unchanged |

- **The AI's role becomes:**
  - draft the brief (P13.1);
  - ask domain questions (P14.1);
  - explain results in plain words;
  - propose and run supporting or custom actions;
  - optionally write the primary code itself ("AI writes the code" mode), with the reference script as the fallback after failed repairs.
- **Task-awareness:** the metric sub-goals (`metric_present roc_auc`) become `metric_present primary` with the metric chosen by task type, recorded as a fact (`task.type`, `task.n_classes`, `primary_metric`).
- **Author decision D14-1 (scientific):**
  - **(a)** reference code is the default and the AI writes code only on request;
  - **(b)** AI-written code is the default with reference fallback;
  - **(c)** always run both and compare.

  This determines what the paper may claim as "LLM-executed".

#### P14.3 Autopilot: from event to event without stopping

- **Run (key `a`, or the first card "Run the study"):**
  1. the engine runs the current event's primary action;
  2. checks sub-goals;
  3. runs required supporting actions;
  4. enters the next event;
  5. repeats.
- **It stops only for:**
  - **(1) a question** (P14.1);
  - **(2) one of three approvals, shown as plain summaries:**
    - "Approve the study brief" (setup);
    - "Approve the chosen model" (validate, shows the metric table);
    - "Run the final test once" (test unlock: the UNLOCK TEST phrase becomes a confirm button with the consequence stated; the logged phrase stays);
  - **(3) a failure** after repairs, with a plain reason and recovery options, presented as a question;
  - **(4) the budget.**
- **Step mode** (the current card UI) stays available. Space pauses autopilot after the running step.
- **Progress:** the horizontal activity flow shows each step; the left list turns green event by event.
- **Gates and invariants are unchanged:** the test stays sealed, fits happen on train only, and every action is still a logged step.

#### P14.4 Generic data rules (engine, no model)

Each rule runs on the registered table after setup and raises a P14.1 question with a recommended answer only when triggered.

| Trigger (generic) | Question (plain words) | Recommended |
|---|---|---|
| Outcome values that differ only in case, whitespace or trailing punctuation | "These look like the same outcome written differently: merge them?" | Merge |
| Outcome with > 2 classes | "Predict all N groups, or one group against the rest?" | All groups |
| A class under 1% of rows, or fewer than 10 rows | "Group X is very rare: keep it, merge it with 'other', or drop it?" | Keep |
| A column that determines the outcome (perfect mapping, a deterministic function, or the name contains the outcome name) | "Column X seems to contain the answer; using it would make results meaningless. Exclude it?" | Exclude |
| Two outcome-like columns | "Which one is the outcome? The other will be excluded." | The higher-ranked one |
| An identifier column (unique per row, non-float) | "X looks like an ID: exclude it from prediction?" | Exclude |
| Repeated values of a likely subject column, with brief `repeated_subjects` ≠ no | "Do rows with the same X belong to the same person or unit?" | Yes, use it as the group |
| Exact duplicate rows > 0 | "N rows are exact copies: remove them?" | Remove |
| A column > 50% missing | "X is mostly empty: drop it?" | Drop |
| Survival: negative or zero times; event column not binary | "Some times are ≤ 0: drop those rows?" | Drop |

Answers become recorded decisions (`DataDecision`) that the reference scripts read, and the Methods report lists them.

#### P14.5 Plain language for non-experts

- Every event title gets one line: "What happens here and why it matters" (≤ 15 words), from the template.
- A glossary is shown on hover or with `?` (split, validation, test, leakage, ROC AUC, C-index). There is no jargon in questions.
- Results are explained after each scoring step: the Navigator writes two sentences from the recorded metrics. A built-in sentence template is used when no model is connected.

#### P14.6 Robust with weak free models

- The Navigator never blocks progress: on invalid output, use the reference path and record a plain-language note.
- Responses are short structured JSON with one repair; schema-constrained output is used where the provider supports it.
- The Models panel shows "Recommended for MLCA" by measured success (P14.7), not by price only.

#### P14.7 Acceptance: real runs, not more unit tests

- `scripts/acceptance_run.py` drives the TUI headless (pilot) through autopilot from `mlca init` to Report, for each table in `benchmark_datasets/`. Configurations: **(a)** no model; **(b)** `openrouter/free`; **(c)** the author's chosen model.
- **Recorded per run:** each stop (question, approval or failure), the answers used (recommended), time, model calls and tokens, and the final metrics. The output is `acceptance/<date>/summary.csv`.
- **Pass:** zero failures, and stops limited to triggered questions plus the three approvals, on every table in configuration (a). Configuration (b) may degrade AI text but never blocks.
- The unit suite is kept as a regression guard only. New work is judged by acceptance runs.
- This doubles as evidence for R1-1/R1-2/R2-2 (completion, interventions, time and cost) if the author chooses.

#### P14.8 Order of work

1. **P14.2** reference scripts plus task-aware metrics: removes the hard dependency on model-written code.
2. **P14.4** generic data rules plus `DataDecision`.
3. **P14.1** Ask records, docked panel, and Navigator and Worker asks.
4. **P14.3** autopilot with the three approvals.
5. **P14.5** plain language; **P14.6** robustness.
6. **P14.7** acceptance runs; then brain-mode parity (MCP questions).

#### P14.9 Decisions for the author

- **D14-1:** reference code versus AI-written code as the default (P14.2).
- **D14-2:** whether Esc ("use recommended") is allowed for leakage and outcome-merge questions, or those always need an explicit answer.
- **D14-3:** whether autopilot may run the alternative model by default (it adds time, but gives the comparison).

### P15: the adventure loop (replaces P14.1, P14.3 and P14.5)

**Idea.** A game master describes the scene and offers a few moves; the player picks one; the dice and rules decide what happens. In MLCA:

| Game | MLCA |
|---|---|
| The rules | The engine: events, gates, checks, test lock (unchanged) |
| The game master | The Navigator: one short fixed prompt per turn |
| The scene | Where the study is, in one line |
| The moves | 2–4 choices, recommended first, plus "Your own move" (custom) |
| Rolling the dice | The Worker writes the code; MLCA runs it on this machine and checks it |
| The narration | Two sentences on what happened, from recorded outputs |

**One turn.**
1. The engine builds the state view: event, sub-goals, facts, last result.
2. The Navigator answers one fixed prompt (≤ 25 lines) with a scene JSON: `situation`, `moves[2–4]` (catalogue action, title ≤ 8 words, `what_happens` ≤ 20 words, `recommended`), and an optional `question` (P14.1 format).
3. The engine validates the scene against the catalogue and gates. If it is invalid, the template defaults are shown at once, and the turn is never blocked (P14.6).
4. The user picks a move: a number key, or Enter for the recommended one. Autopilot (`a`) picks the recommended move until a question, an approval or a failure.
5. The step runs: Worker code, the run, the checks.
6. The Navigator narrates in two sentences; the activity flow shows it.

**Prompts.** These are the only prompts, each short and fixed: scene, question, worker code, repair, narration, brief draft. The event and action text stays in the templates (Do / Save / Record). Prompt text is versioned with the package and recorded per request (already logged), so the measured runs can cite the exact prompts.

**Model access (recommended 2026-10-13, awaiting the author).**
- Keep the `openai` Python client against OpenRouter's OpenAI-compatible Chat Completions API. The same code serves OpenAI, local models and the ChatGPT plan.
- Do not adopt the OpenRouter Agent SDK. Its value is a model-driven tool loop, while MLCA's design and the paper's contribution (R2-1) is that the engine owns the loop and the model answers one structured question per turn.
- **Use these OpenRouter request features through `extra_body`:**
  - `provider.require_parameters: true` whenever `response_format` is sent, so requests route only to providers that honour structured output;
  - `response_format` JSON schema switched on automatically when the catalogue says the model supports it (`json_output`);
  - optional `provider.data_collection: "deny"` / `zdr` in Privacy (R1-6b);
  - record the `model` and `provider` OpenRouter reports for every response;
  - no `models` fallback list sent by MLCA (P16.4 rule 5 governs; the `openrouter/free` router remains the user's explicit choice).

**Code execution.** Scripts already run on this machine. Level A wraps them with bubblewrap (no network, only declared files); level B runs them directly with an audit hook. **D15-1 (author):** the default, keeping level A where available (the paper's safeguard claims rely on it, R1-5/R1-6b) or level B everywhere.

**Order.** After the revision cut (`mlca bench` on real models, frozen version). P15 is product work; the measured runs use the version frozen before it.

---

### P16: complete token and cost accounting per project, plus OpenRouter request settings

**For the implementing agent.** This is on the revision path: it must land **before** the code freeze, because the measured runs (R1-4, R2-2) report these numbers.
- Work in `mlca-revized` on branch `native-onboarding`. Another agent may have uncommitted edits: run `git status` first and touch only the files named here.
- Do not publish, push or tag.
- Keep every new field optional: older projects and the scripted `fake` provider must still load and replay.
- Unknown values stay `null`, never `0`.

**Already present (do not rebuild):**
- `llm/client.py` writes one record per request to `.mlca/requests/<request_id>.json`; `llm/usage.py` rebuilds `usage.jsonl` / `egress.jsonl` from them.
- Fields today: `input_tokens`, `output_tokens`, `cached_tokens`, `cost_usd` with `cost_source`, `model_reported`, `latency_ms`, `request_settings`, plus role/event/step/principal from `RequestContext`.
- `llm/providers/openai_compatible.py` uses the `openai` client and reads `usage.cost`; `provider_request_id` is the response `id` (OpenRouter's generation ID).
- The CLI has `mlca usage` (session usage), `mlca usage import` (Claude/Codex session files, brain mode) and `mlca metrics`.

#### P16.1 Record the full usage OpenRouter returns

OpenRouter returns usage on every response; `usage: {include: true}` is deprecated and must not be sent (docs: Usage Accounting, checked 2026-10-13).

- In `CompatibleProvider.complete`, also return:
  - `reasoning_tokens` = `usage.completion_tokens_details.reasoning_tokens` (already counted inside `completion_tokens`; store it separately, never add it twice);
  - `cache_write_tokens` = `usage.prompt_tokens_details.cache_write_tokens`;
  - `upstream_cost_usd` = `usage.cost_details.upstream_inference_cost`;
  - `provider_reported` = the top-level `provider` field of the OpenRouter response body.
- Check that `response.model_dump()` keeps OpenRouter's extra fields; otherwise read `response.model_extra`. Add a unit test with a recorded response body.
- In `client.py`, also persist `provider_request_id` (today the adapter returns it but the client drops it; P16.5 backfill depends on it). Then add these four fields to the request record, initialised to `None`, set from `result` like `input_tokens`. Pass `provider_reported` through `redact_value`.
- Do the same in `openai_chatgpt.py` where the Responses API provides the equivalent fields (`output_tokens_details.reasoning_tokens`); otherwise leave them `None`.

#### P16.2 Project totals, per-model breakdown and export

- In `usage.summary()`, stop turning missing values into `0`. For every token and cost field, report the sum of known values plus `unknown_<field>_requests` (the count of records where it is `null`), and mark a total `partial: true` when that count is above zero. Then add:
  - `reasoning_tokens`, `cache_write_tokens` and `upstream_cost_usd` to each group;
  - the axes `model_reported` and `provider_reported` beside `role`, `event_id`, `step_id` and `principal`;
  - a top-level `totals` block: requests, input, output, reasoning, cached and cache-write tokens, known cost, unknown-cost requests, latency.
- `mlca usage` prints the totals and one line per reported model. `mlca usage --csv <file>` writes one row per request with every record field (no payloads). The project's `project_id` (from `.mlca/project.yaml`) goes on each row so CSVs from several projects can be merged.
- `mlca metrics` and `mlca bench summarize` include `reasoning_tokens` and `cache_write_tokens` wherever they report input and output tokens. Reuse `usage.summary()`; do not compute tokens a second way.

#### P16.3 Stable pseudonymous `user` per project

- Send `user` on every OpenRouter chat request: `"mlca-" + sha256(project_id)[:16]`. This isolates provider abuse blocks per project and lets OpenRouter attribute requests (docs: User Tracking).
- It must contain no name, path or e-mail.
- Record the value in the request record as `end_user`.
- Send it only to OpenRouter (`provider_config.kind == "openrouter"`).

#### P16.4 OpenRouter request settings

All go through the `openai` client's `extra_body`, only when `kind == "openrouter"`:

1. **Structured output on automatically.**
   - Change `ProviderConfig.structured_outputs` from `bool = False` to `bool | None = None`, where `None` means auto.
   - Auto = on when the cached catalogue lists the model with `json_output` (`catalog.cached(provider)`, P-catalog work of 2026-10-13); otherwise off. An explicit `true`/`false` in config wins.
2. **Only providers that honour it.** Whenever `response_format` is sent, add `provider: {"require_parameters": true}`.
3. **Privacy (R1-6b).**
   - Add `Privacy.provider_data_collection: Literal["allow", "deny"] | None = None` and `Privacy.zero_data_retention: bool = False`.
   - Map them to `provider.data_collection` and `provider.zdr`.
   - Show both in the Models panel under "Advanced". Record the settings used in `request_settings`.
4. **Record what answered:** `model_reported` (exists) and `provider_reported` (P16.1).
5. **No silent fallbacks.** Never send a `models` fallback list or `provider.allow_fallbacks` changes from MLCA code, so a measured run always reports the model it asked for. The `openrouter/free` router is the user's explicit choice and stays allowed.

#### P16.5 Cross-check against OpenRouter's own records

- `mlca usage backfill`: for records with a `provider_request_id` but a missing `cost_usd` (timeouts, interrupted runs), call `GET /api/v1/generation?id=<id>` with the stored credential. Fill the missing usage fields with `cost_source: "generation_endpoint"`; never overwrite provider-returned values. Rate-limit (1 request/s) and skip records older than 30 days. Requests that failed before a response (no generation ID) cannot be recovered; list them as `unrecoverable` in the output.
- `mlca usage reconcile <activity.csv>`: the author exports the CSV from openrouter.ai/activity (time period, grouped by Model; docs: Activity Export).
  - **Ask the author for one real export file before writing the parser.** The column names are not documented.
  - Compare per model and per day: requests, tokens and spend against the MLCA ledger for the same window.
  - Print the differences, and write `reconcile.json` beside the CSV.
  - The Activity page includes all usage on the account, so differences are expected unless the runs used a dedicated API key. Report them; never "fix" the ledger from the export.
- **Recommendation for measured runs (author action, not code):** create a dedicated OpenRouter API key per measurement batch. The Activity export grouped by API key then gives an independent total for exactly those runs.

#### P16.6 Tests and acceptance

- **Unit tests:**
  - a recorded OpenRouter response body with reasoning, cache-write and upstream-cost fields → all recorded;
  - a response without them → `None`, not `0`;
  - `summary()` totals and the per-model axis;
  - the `user` hash is stable per project and differs between projects;
  - `extra_body` contents for each P16.4 combination;
  - `fake` provider records still validate.
- **Acceptance (real, free):** run one `mlca bench` smoke run with `openrouter/free` on one generic table. Then:
  - `mlca usage --csv` lists every request with the reported model and provider;
  - totals equal the sum of rows;
  - `mlca usage backfill` makes no changes when nothing is missing.

  Paste the totals into `docs/DECISIONS.md` with the date.
- **Done when:** the above pass, `ruff check` is clean, and the focused suites pass (`tests/unit`, `tests/integration -k usage or bench or metrics`). The full suite runs once at the end.

#### Answers to the implementing agent (2026-10-13; given by Claude at the author's request, the author may override)

1. **Scope:** ~~the revision cut first; P14 and P15 after the freeze~~ **Superseded 2026-10-13 by the author: P14 (as revised by P15) and P15 are to be built now, before the measurement freeze.** See "Next instructions for the implementing agent" below.
2. **D14-1, code in measured runs:** the Worker writes the code. A Worker failure is a result: record it, never replace it silently with reference code. Reference scripts, if built later, are a separate, labelled no-AI baseline arm with their own runs, never mixed into a Worker run.
3. **D15-1, execution:** keep level A (bubblewrap) where available; level B only by explicit opt-in, as now. The paper's safeguard claims (R1-5, R1-6b) depend on it.
4. **Activity CSV:** the author exports it from openrouter.ai/activity, grouped by Model, for the period of the runs. They save it as `ES/submission2/experiments/10_agent_metrics/openrouter_activity/<YYYY-MM-DD>_by_model.csv` in the paper repository (`/home/prime/Documents/github/v-papers/ml_copilot_paper`). Build the `reconcile` parser only after that file exists. P16.1–P16.4 and backfill do not need it.
5. **Fallback lists:** P16.4 rule 5 governs (P15 text corrected).
6. **Names:** the game metaphor is for explanation only. Code, prompts, CLI and documentation use neutral names (turn, situation, choices, result summary).
7. **Live calls:** none until the author authorises the smoke run.

#### Review of the P16/P14.6 commits and fixes already made (Claude, 2026-10-13)

The commits `8472fb4`, `cb00eec` and `026e203` were reviewed. These issues were fixed directly. They are in the working tree, uncommitted; do not redo them.

1. **Partial totals.** `usage.aggregate` marked every total partial, because providers omit `cache_write_tokens` (no explicit caching) and `upstream_cost_usd` (not BYOK).
   - Now only `CORE_FIELDS` (input tokens, output tokens, cost) set `partial`.
   - `OPTIONAL_FIELDS` report the total of what was reported, plus `reported_requests` / `unreported_requests` (`usage.measured_total`).
2. **Navigator fallbacks hidden in completion rates.**
   - `metrics.navigator_use()` adds a per-run `navigator` section: `proposals_used`, `fallbacks`, `budget_stops` (counted separately) and `fallback_rate`.
   - `bench summarize` reports `navigator_fallback_rate` (distribution), `navigator_fallbacks`, `navigator_budget_stops` and `completed_without_navigator_fallback` beside the completion rate.
3. **Structured output depending on a local file.**
   - One helper, `client.structured_setting(provider_config, model)`, returns `(enabled, source)` with `source` ∈ `config | catalogue | no_catalogue | default`.
   - Each request records `structured_outputs_source`.
   - `bench run` writes `structured_outputs` per role into `bench.json`, after refreshing the catalogue (`model_catalog`).
4. **Tests:** `tests/unit/test_p16_review_fixes.py`. 59 tests in the usage, metrics, bench and Navigator suites pass.

#### Next instructions for the implementing agent (2026-10-13)

Before you start:
- Run the full suite once on the current working tree.
- Commit the uncommitted, tested work as its own commit: P13 TUI changes, `mlca models` / catalogue snapshots, and the review fixes above. Message: "P13 guided TUI, mlca models catalogue snapshots, P16 review fixes".
- Do not mix it with new work.

Then build, in this order, each with its own commit and tests:

1. **P14.4 generic data rules** and `DataDecision` records. No dataset-specific rule: every trigger reads table properties.
2. **P15 turn loop**, which replaces P14.1, P14.3 and P14.5:
   - the situation + choices JSON from one fixed Navigator prompt, validated against the catalogue, with template fallback (P14.6, done);
   - questions in the P14.1 record format;
   - autopilot (`a`) that stops only for questions, the three approvals, failures and the budget;
   - two-sentence result summaries.

   Neutral names in code and documents.
3. **P14.2 reference scripts as a separate, labelled no-AI baseline arm** (answer 2 stands). *Superseded 2026-10-14: the author dropped the reference arm from the comparisons.*
   - Never substitute them inside a Worker run.
   - Record `measurement_arm: reference | worker` in bench manifests and metrics.
4. **P14.7 acceptance runs**, offline configuration (a) only, until the author authorises live calls.

Defaults for the open decisions (Claude's recommendation; the author may override):
- **D14-2:** leakage and outcome-merge questions need an explicit answer; Esc does not accept them.
- **D14-3:** autopilot trains the alternative model too (it gives the comparison).

After P14/P15:
- The measurement freeze, then the authorised smoke run.
- In that run, verify the `/generation` field names used by `mlca usage backfill` against a real response (review point 5). Fix them if they differ.



**Implementation update (2026-10-13):** P16.1–P16.4 and P16.5 metadata backfill are implemented with offline regression tests. P16.5 Activity reconciliation waits for the author's real CSV; no parser was guessed. P16.6 live acceptance waits for explicit authorization. P14.6 now offers template choices after Navigator failure (bounded JSON repair, safe failure metadata), while integrity errors still stop and Worker failures remain results. No reference scripts or P15 loop were added. Full offline working-tree suite: **245 passed, 1 skipped in 678.51 s** (PowerShell unavailable). Ruff lint and formatting pass. The isolated selective P16/P14.6 candidate passed 34 tests, independently of the other uncommitted work. Local phase commits: `8472fb4` (P16), `cb00eec` (P14.6). Details are in docs/P16_ACCOUNTING.md and the implementation status.


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
| D3 | PyPI/npm package name | `mlcagent` | ✅ author chose `mlcagent` on 2026-10-07; command/import remain `mlca`. Authorized beta PyPI upload awaits validation; npm publishing remains unauthorized |
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

## 2026-10-07 — Author-approved replacement distribution

The author chose `mlcagent` for the 0.2.0b1 PyPI beta, superseding `mlca` and the suggested legacy name. The executable, imports, MCP tools and state folders remain `mlca`. Wrapper identities, installers and metadata now use `mlcagent`. The earlier rejected upload is retained above as historical evidence. One beta PyPI upload is authorized after release validation; GitHub pushes, new remotes and npm publication are not authorized.

## 2026-10-07 — P10 and mlcagent beta release gates

P10.1–P10.7 are implemented. Final full offline suite: **137 passed, 1 skipped in 603.43 s** (PowerShell unavailable); supporting-action/failure targeted subset: 20 passed. Ruff lint/format, approved-name/version guard, wrapper synchronization, build/Twine and 186-entry wheel resource checks pass. The final isolated HOME/XDG wheel walkthrough passes install/version/doctor, synthetic init, Claude project/skill permission preview without writes, bubblewrap namespace probe and stdio discovery of all 14 tools. No live models, original anemia data or native client/OS validation were performed. The authorized PyPI upload as `mlcagent` 0.2.0b1 follows; npm/GitHub operations remain unauthorized.

## 2026-10-07 — Published-beta verification

[PyPI release](https://pypi.org/project/mlcagent/0.2.0b1/). Fresh PyPI verification used an empty temporary HOME/XDG and uv cache: `uv tool install mlcagent==0.2.0b1`, `mlca --version` (0.2.0b1), `mlca doctor --json` (level A capability; execution must confirm isolation), and `mlca mcp doctor` (14 tools) all passed. Published wheel/sdist SHA256 hashes match the scanned release artifacts. Local tag `v0.2.0b1` points to release source `16bcc72`; no push. P10 is complete, while M7, real providers/data, and native macOS/Windows remain pending. The beta description contains an overlooked historical README Status paragraph; it is corrected in source for the next release, with no second upload. Token rotation to a project-scoped token and removal of the account-wide file remain an author account step; the file was read only by the publish command.

### P17: bench pacing (done) and `mlca bio-bench` for the paper's own case studies

**Done 2026-10-14 (Claude, uncommitted).** These protect `mlca bench` against provider limits:
- **Pacing.** `ProviderConfig.requests_per_minute` paces every request (default 16/min for OpenRouter free models, whose account limit is 20/min). The window is shared by all MLCA processes.
- **Rate limits.** A 429 waits for `Retry-After`, or 5/15/30/60 s, without spending an attempt.
- **Provider errors.** A provider error ends a Worker step as `provider_error`, never as a code repair.
- **No JSON-capable provider.** A 404 for that reason retries once without JSON mode, and remembers that for the session.
- **Cooldown.** Guided bench runs wait `cooldown_s` (default 600) and retry the step, up to `max_cooldowns` (3) times.
- **Accounting.** All waiting is reported as `time.provider_wait_s`, never as model or engine time.
- **Tests:** `tests/integration/test_provider_resilience.py`.

**Why `bio-bench`.** `mlca bench` runs one generic table through the `tabular_classification` or `survival` template. The paper's case studies are multi-stage protocols: unsupervised discovery, labels derived from it, supervised models with repeated splits, then an external cohort and survival analysis. They also need custom instructions beside the template steps. `bio-bench` measures MLCA on those.

**Case study 1 (HNSCC), from the legacy script** `mlca_experiments/jun16_copilot_agent_results_case_study1.py`:

| # | Legacy step | Legacy detail |
|---|---|---|
| 1 | Load | TCGA expression `tcga.survival.fcptac.csv` (415 patients) + `survival_tcga.csv`; CPTAC `cptac.survival.fcptac.csv` (102) + `survival_cptac.csv`; in `mlca_experiments/hnscc_mlca/data/Case-Study-HNSCC-ML-Copilot-Agent/processed_data/` |
| 2 | Discover | KMeans, agglomerative (ward) and GMM × k = 2–10 on **all** TCGA patients; silhouette, Calinski–Harabasz, Davies–Bouldin, inertia |
| 3 | Select | the configuration with the **lowest survival log-rank p-value** |
| 4 | Label | the two largest clusters → 0/1 |
| 5 | Classify | `RUNS` random train/test splits; SelectKBest(f_classif) fitted on train; 5 classifiers (LR, RF, SVM, KNN, GB) × feature sizes |
| 6 | External | predict CPTAC labels; Kaplan–Meier / log-rank on the predicted groups |
| 7 | Report | metric distributions, ROC curves, KM plots |

The file holds two versions: k 2–10, 100 runs, sizes {2…15}; and k 2–8, 50 runs, sizes {2…20}. The paper reports "100 runs". `hnscc_mlca/mlca_conversations/` holds seven short JSON logs (30 Aug 2025). They were written by a coding agent porting the Colab notebook "with MLCA-style logging"; they are **not** ML Copilot v1 logs (corrected 2026-10-14).

**Integrity points the legacy protocol has (R2-4):**
- Steps 2 and 3 use all TCGA patients, including those later used as test rows (transductive labels).
- Step 3 selects the clustering by the survival outcome that is reported afterwards, which makes the survival separation optimistic.
- Neither invalidates a re-run; both must be stated, and the revised protocol must choose (D17-1, D17-2).

**Design (generic, not HNSCC-specific).**
1. **Template `subtype_discovery`.** Events: onboard → data (two registered tables with roles `discovery` and `external`) → split (patient-level, discovery cohort only) → discover → label → features → model → validate (repeated splits) → external (sealed like `test`; one exposure) → report.
   - Engine additions: table roles; an `external` partition locked like `test`; an action that runs N repeated splits and records the distribution; unsupervised actions that need no target at onboard (survival columns only).
2. **`mlca bio-bench <card>`.** The same driver as bench (pacing, cooldowns, metrics, arms). The card adds:
   - the case-study protocol (k range, methods, selection rule, N, feature sizes, classifiers);
   - an ordered list of custom instructions for steps outside the template;
   - a legacy-comparison file mapping each reported legacy number to its source, so the run reports agreement or difference per number.
3. **Arms.** `worker` (the AI writes the code). The `reference` arm is dropped (author, 2026-10-14).

**Order.** CS1 (HNSCC) end to end first. Then decide whether CS2 (LUAD transfer), CS3 (BRCA receptors) and CS4 (anemia) follow, or stay legacy-described in the paper.

**Decisions for the author:**
- **D17-1 selection rule:** **(a)** replicate the legacy rule (lowest survival p) for comparability; **(b)** internal metrics only (e.g. best silhouette), prespecified; **(c)** both as labelled variants.
- **D17-2 discovery data:** **(a)** all TCGA patients as in the legacy run; **(b)** training patients only, assigning held-out and CPTAC patients with the fitted model.
- **D17-3 repeats:** 100 (as the paper states) or 50 (the second legacy version).
- **D17-4 scope:** CS1 only before resubmission, or more case studies.

**P17 layout update (2026-10-14).**
- Bench tables moved into this repository: `benchmarks/datasets/`.
- Bench cards and runs, and the bio-bench protocols (S1–S4, `STUDY.md`), moved to `../mlcagent-experiments/`. Full private planning versions there are `*.local.md` and are never pushed.
- The paper repository keeps only curated results and figure scripts.

### P18: wrap-up roadmap: finish MLCA v2, run the comparisons, close the paper (2026-10-14)

**For the implementing agent: start here.**
- Work on `master` (fast-forwarded to `native-onboarding`, `f430270`).
- No push, publish, live model call or upload without the author's go-ahead.
- Runs, cards and protocols live in `../mlcagent-experiments/`; read its `AGENTS.md`, which carries the bio-bench rule and the custom-instruction rule. MCP details are in `plan_mcp.md` §14.

#### State on 2026-10-14

**Done:**
- P0–P8 core; MCP M0–M6 and MX1–MX6; P10 metrics;
- P13 guided TUI; P14.2 reference arm; P14.4 data review; P14.6; P15 turn loop;
- P16 accounting with review fixes; **P17 part 1 only** (pacing, rate-limit waits, cooldown); `mlca models` catalogue snapshots;
- `benchmarks/datasets/`.

Suite: 270 passed, 1 skipped.

**Not done:**
- No live model run has completed: the two smoke runs stopped on provider rate limits.
- M7 has never run.
- Brain-mode bench does not exist (`plan_mcp.md` §14).
- **P17 part 2 is not built:** E1 external cohort and E2 bio-bench driver.

#### Phase A: code, before the freeze (order matters)

| # | Item | Why | Done when |
|---|---|---|---|
| A1 | **Leakage fix in the data review.** Outcome-dependent checks (feature-outcome mapping, perfect numeric separation) run **after the split on training rows only**. Outcome-free checks (identifiers, duplicates, missingness, label spellings, event coding) stay before the split | Integrity (R2-4); today all checks use all rows, including future test rows | test: a planted leaky column is found from training rows; test rows are never read before the split |
| A2 | **Perfect-separation default.** Recommend "Exclude" only for name matches or a one-to-one categorical mapping. For a numeric column that separates the classes perfectly, recommend "Keep and flag in the report". Keep the explicit answer | Avoids removing a real strong predictor by default (**author to confirm**) | test per case |
| A3 | **Readable CLI errors.** `mlca bench run` and other commands print the actual validation message instead of "Action failed" | the first smoke attempt failed silently | test with an invalid card |
| A4 | **Brain-mode bench MB1–MB5** (`plan_mcp.md` §14) | the driver vs brain × 5-model comparison | §14.4 |
| A5 | **E1 external cohort.** A second registered table with role `external`, sealed like `test`; readable only after the test unlock by the test/interpret events and their custom instructions; scored once per variant | bio-bench S3, S4 | tests: unreadable before unlock; one exposure recorded |
| A6 | **E2 `bio-bench` driver.** `mlca bio-bench run <card>` = bench plus `custom_instructions: [{event, text}]` issued in order (driver: `session.custom`; brain: in the prompt file), with questions and approvals as policy. It exports `custom_instructions.md` per run: verbatim text, event, model, scope decision, resulting step, outcome, word count | bio-bench; custom instructions are published research artefacts | test with scripted models |
| A7 | **Run export.** `mlca bench export <out> --to <dir>` copies the curated subset (scripts, `.mlca/llm`, `log`, `steps`, reports, figures, `metrics.json`, `usage.csv`, `bench.json`, `custom_instructions.md`) and never `.mlca/private|env|data` | experiments repo and paper results | test |
| A8 | **Smoke runs** (author go-ahead; free models, with a few dollars of credit if rate limits persist): driver on `heart_disease` with `nvidia/nemotron-3-super-120b-a12b:free`, then MB6 brain mode per client | the first proof that the AI path completes | each run completes or fails with a recorded category |
| A9 | **Freeze.** Version `0.2.0` (or `0.3.0b1`); tag; CHANGELOG; fix the stale PyPI Status paragraph; publish only on request | every reported number comes from one version | tag exists; the experiments repo records the commit |

#### Phase B: evidence runs (after A9; experiments repo)

- **B1.** `PREREGISTRATION.md` committed in `mlcagent-experiments/` before measured runs: models (exact IDs and catalogue snapshot), cards, N, settings, approval policy, budgets, metrics, failure rules.
- **B2. `mlca bench`, the 6 tables:**
  - driver arm × 6 models;
  - brain arm via OpenCode × the same free models;
  - Claude Code × Haiku 5.5;
  - Codex × GPT-6 Luna;
  - N per cell set in B1.
- **B3. Bio-bench** (each study's data-prep script first; `STUDY.md` protocols):
  - S1 anemia and S2 receptors (6 tasks) in all arms;
  - S3 PAM50 and S4 HNSCC after A5/A6.

  A step MLCA cannot achieve is recorded as *not achieved*; that is acceptable.
- **B4.** `mlca usage backfill`: verify the `/generation` field names on a real response. `mlca usage reconcile` against the author's OpenRouter Activity CSV, ideally with one API key per batch.
- **B5.** Per-study `summary/` tables; curated copies into the paper's `ES/submission2/experiments/results/`; the results ledger and figure scripts there.

#### Phase C: paper (paper repository; the author decides wording)

- **C1. Author decisions:**
  - the study order and dropping CS2 / Appendix A;
  - S4 clustering rule, data scope and repeats;
  - S1 haemoglobin;
  - S2 HER2 evaluation;
  - S3 harmonisation;
  - the final models;
  - A2.
- **C2. Answers to open provenance questions:** producers, the `anemia.csv` source, the 12-gene panel, the Discussion numbers without a file.
- **C3.** Comment-by-comment edits and responses, E-1 first. Comments that need no runs first (presentation, references, appendices, TCGA definition, Fig. 1, CS4 text corrections).
- **C4.** New results enter the manuscript only from the ledger.
- **C5.** Cover letter → portal package → final sweep → author upload. Deadline 4 January 2027.

**Can run in parallel with A:** C1–C3 for comments that need no runs.


### Remaining work order: finish P17, then P18, in one run (2026-10-14; supersedes the Phase A order above)

**Execution status (14 October):** WP1–WP7 finished locally. Final code suite: 296 passed,
1 skipped; experiments: 7 passed. All seven reference attempts recorded zero model calls and
passed export auditing. S1 core completed with custom instructions not achieved; S2 retained
four interpretation timeouts and two HER2 bootstrap NaN failures. Stopped after package 7.
No measurement freeze, live calls, push, publication or upload. `master` began at f430270.
See docs/IMPLEMENTATION_STATUS.md; older deferral/status notes are historical.

All remaining work, given at once. **P17 is completed first (package 1)**, then the P18 packages 2–7, without waiting between packages. Each package ends with its tests passing and **one local commit** in the repository named. A short progress note after each package (what changed, tests run, blockers) is enough; stop only after package 7 or on a real blocker.

**Limits for every package:**
- no live model calls, pushes, remotes, publishing or uploads;
- do not edit the paper repository;
- never commit `*.local.md`;
- keep the bio-bench rule (a step MLCA cannot achieve is recorded as *not achieved*) and the custom-instruction rule (verbatim artefacts).

**Decisions already made** (Claude, at the author's request; the author may override):
- **A2:** recommend "Exclude" only for a name match or a one-to-one categorical mapping; a numeric column that separates the classes perfectly gets "Keep and flag in the report".
- **E3 is not built.** Within-study repeated splits stay a custom instruction (S2 CI-3, S4 B3): they show custom instructions at work and need no engine change.
- **Brain-mode clients:** OpenCode (the same OpenRouter models as driver mode), Claude Code and Codex.

| # | Repository | Content | Acceptance |
|---|---|---|---|
| **1 · P17 part 2: bio-bench engine (finish P17 first)** | `mlca-revized` | **E1:** registered table role `external`, sealed like `test`; readable after the test unlock by the test/interpret events, built-in actions and custom instructions; one exposure per variant, logged. **E2:** `mlca bio-bench run <card>` with `custom_instructions: [{event, text}]` issued in order (driver: `session.custom`) and questions and approvals as policy. It writes `custom_instructions.md` per run: verbatim text, event, step, model, scope decision and reason, outcome, word count. A refused or failed instruction is recorded, never retried silently | scripted-model tests for both; E1 unreadable before unlock; refusals appear in the export |
| **2 · Integrity and errors** | `mlca-revized` | **A1:** outcome-dependent data checks after the split, on training rows only; outcome-free checks stay before the split. **A2** as decided. **A3:** the CLI prints the real validation or engine message instead of "Action failed" | tests: a planted leaky column is caught from training rows and test rows are never read before the split; the A2 recommendation per case; an invalid task card shows the field error. Full suite passes |
| **3 · Brain-mode bench** | `mlca-revized` | `plan_mcp.md` §14 **MB1–MB5**: OpenCode registration, an isolated client config per run (only MLCA tools), `mlca bench run --mode brain --client …` and `mlca bio-bench run --mode brain …` (custom instructions go into the prompt file), the policy approver, client usage capture, and a summary across arms. Check every client flag with `--help` | §14.4 offline tests using recorded client outputs as fixtures. MB6 (live) is **not** run |
| **4 · Run export** | `mlca-revized` | `mlca bench export <bench-output> --to <dir>` (also for bio-bench): copies scripts, `.mlca/log`, `steps`, `llm`, `requests`, reports, figures, `metrics.json`, `usage.csv`, `bench.json`, `custom_instructions.md`; never `.mlca/private`, `env` or `data` | test: excluded paths are absent; files match their sources |
| **5 · Experiment material** | `mlcagent-experiments` | **Prep scripts:** `bio-bench/S2…S4/prepare_data.py` per each `STUDY.md` (deterministic, no AI). They read `SOURCE_DATA` from `paths.local.yaml`, write to `data_prep/`, and record input/output SHA-256 and counts; S1 gets a checksum-only script. **Task cards:** `bench/cards/` for the 6 tables (driver, plus a brain variant per client) and `bio-bench/S*/task_card.yaml` (driver and brain). **`PREREGISTRATION.md` draft** (models, catalogue snapshot, cards, N, settings, approval policy, budgets, metrics, failure rules), marked DRAFT until the author approves. A summary script skeleton that builds the cross-arm tables from exports | prep scripts reproduce the expected counts (S2 ER 81/39, PR 68/47, HER2 15/107; S4 415/102); all cards validate (`TaskCard` + `Config`) |
| **6 · Status docs** | `mlca-revized` | Refresh `docs/HANDOFF.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/mcp.md` and the status lines in `plan_mcp.md`. The remote is `HawkFranklin-Research/mlcagent`; `master` = `f430270`; P13–P16 and P14.2/P14.4/P15 are done; P17 is half done. **No freeze exists yet:** moving `master` is not a freeze | the docs agree with `git log` and with this work order |
| **7 · Offline acceptance, then stop** | both | Full suite. Offline **reference-arm** runs of S1 and S2 (6 tasks) through `mlca bio-bench` with zero model calls, exported with WP4 into `mlcagent-experiments/bio-bench/S*/runs/reference/`. Then **stop and report** | suite passes; the reference runs complete or record *not achieved* steps; zero model requests in `mlca usage` |

**After package 7 (author's go-ahead needed):**
1. Live smoke runs: driver with `nvidia/nemotron-3-super-120b-a12b:free`, then MB6, one brain-mode run per client.
2. Fixes from the smoke runs.
3. The freeze (A9: version, tag, CHANGELOG, PyPI description).
4. `PREREGISTRATION.md` final and committed.
5. The measured runs (Phase B).
