# Work order 04: Part A

Historical completion snapshot; Part B subsequently started. See the current
HANDOFF and experiments/bench/dev-loop/ reports for live development status.

Author boundary (16 October 2026): finish and validate Part A first. The author
subsequently authorized Part B while sleeping; its inference runs have not started. This report describes software implementation and synthetic offline
checks, not completed AI experiments or scientific evaluation results.

## Implemented

- A1: validated, scoped, versioned rails snapshots and engine firing records;
  local commit `0bdeb79`. Baseline `rails-0.0`, with no failure-derived rails yet.
- A2: regression, multiple categorical outputs, clustering and representation
  templates; excluded-label registration and local per-row evaluator artifacts;
  local commit `6c0576e`. Separate external scoring lives in experiments commit
  `e7eef1e` and is explicitly not agent work.
- A3: `mlca run` infers a study from a file/folder and brief, validates it, creates
  fresh independent projects, uses existing Session decisions and safeguards,
  preserves failures, and exits nonzero if any run fails. No researcher manifest
  enters the run. Input discovery is stable across repetitions.
- A4: CLI/TUI decision countdown and Halt; human alternatives and scoped custom
  instructions use the same engine validation. Policy and human actors remain
  distinct. A Halt pauses before the next action, not inside a running script.
- A5: inference choices, questions, halts/overrides by event, rails/hash/firings,
  actual router model mix and setup-inference usage in project/bench metrics.
  Missing measurement stays unavailable. Setup cancellation retains its evidence.

## Verification

Final full-suite result: **380 passed, 1 skipped in 1189.07 seconds**
(PowerShell unavailable). Ruff lint/changed-file formatting and whitespace checks
pass. Local A3 commit `fb8abf2`; A4 commit `6c7d3aa`; A5 records this report.
External synthetic scorer checks: **2 passed in 1.51 seconds**.
Focused checks cover bare-CSV completion, poisoned-manifest exclusion, new
workflow completion, excluded external-table sealing, inference validation,
CLI exit codes, decision expiry/halt/override, a TUI keyboard Halt, provider
cooldowns, failed independent setups, output-discovery stability and sourced
metrics. Ruff and whitespace checks run before local commits.

## Remaining and limits

- Part B: live 12-table development, failure-derived rails and acceptance are
  authorized after Part A validation; their results belong in the separate loop report.
- Part C: the live development/rails review package follows Part B.
- No held-out evaluation, measurement freeze, model calls, publishing or push.
- Automatic CLI OpenRouter onboarding is recorded in plan.md as later work.
- Four new templates are scripted-fixture tested; live method reliability is
  unmeasured. There is no claim that Part A establishes research performance.
- Covertype, held-out data and author work-order prompt files remain untracked
  and are preserved; private/local notes are not committed.
