# Rails ledger

## Baseline: rails-0.0

The prompts, templates and engine checks at ad92ebd form the historical baseline.
No historical prompt has been moved into an instruction rail. Fresh development entries follow below. The prior Nemotron batch remains development
evidence, not a frozen evaluation. New entries must identify the run, actual model,
event, step, category, value-free diagnosis, files, commit and fresh verification.


## B-0001 — 16 October 2026 — engine setup-contract and accounting fix

- Evidence: `../mlcagent-experiments/bench/dev-loop/round-01/REVIEW.md` and
  `round.json`; original setup request/response envelopes are kept under each
  table and hashed in `setup-evidence/MANIFEST.csv`.
- Eleven setup failures, before any project/Worker step: breast_cancer_diagnostic,
  heart_disease_cleveland, abalone, energy_efficiency, seeds, dry_bean,
  optical_digits, adult, anuran_calls, bike_sharing_hourly, online_retail.
- Actual model mix: Nemotron nano/super/lightning, Dots preview, Laguna and
  Cohere North (exact provider IDs in round.json). Event: onboard; step: none;
  original categories: invalid_inference or runtime_error:ValidationError.
- Value-free error: inference passed the advertised schema but failed a later
  hidden constraint (metric identifier, incomplete alternative or task cardinality).
- Diagnosis: engine response schema and semantic validation were inconsistent.
  No scientific rule is weakened. Advertise complete nonrecursive alternatives
  and allowed metric identifiers, and validate local table constraints inside
  the existing one-repair structured path. Local validation context is never
  included in the provider request.
- Accounting: preserve known request/tokens/cost/latency/model distribution when
  setup fails before a project exists. Unknown compute time stays unavailable.
- Files: autonomous/inference.py, autonomous/runner.py, llm/structured.py,
  evaluation/bench.py; regressions: integration/test_setup_contract.py.
- Rails set after engine fix: rails-0.1. Commit: `c5ea681`.
- Verification: synthetic invalid metric, incomplete alternative, unknown-column
  and task-cardinality responses repair once or fail with invalid_inference;
  zero raw-row context sent. Fresh live verification pending.

## L-0001 — 16 October 2026 — RL-0001 (instruction)

- Evidence: `../mlcagent-experiments/bench/dev-loop/round-01/covertype/setup-001/`;
  hashed copies in round-01/setup-evidence/covertype/setup-001/.
- Actual model: poolside/laguna-s-2.1:free. Event: onboard; step: none;
  failure category: output_truncated. A 16,384-token output allocation was
  exhausted before a usable study proposal; no Worker execution occurred.
- Generic cause: unnecessary setup elaboration can consume the response budget.
  Ask for one concise proposal, adding alternatives only for actual unresolved
  scientific ambiguity. This cannot guarantee control over hidden reasoning or
  provider truncation; preserve any further truncation as failure evidence.
- Change: rails/RL-0001.yaml, scoped to Navigator/onboard/all problem types;
  rails-0.2. Commit: `900bd07`.
- Genericity: no table, filename, column, observed value, model or domain in
  instruction or reason. Valid for any study setup; no safeguard is changed.
- Offline verification: genericity and actual inference-request injection tests.
  Fresh live verification pending; do not relabel Round 1 as successful.

## L-0002 — 16 October 2026 — consolidated design pass (RL-0002–RL-0024)

- Proposed by Claude Code; source and the observed (O)/anticipated (A) basis per
  rail are retained in rails/proposed/rails-0.3/DESIGN.md. Author review at Part C.
- Observed causes: rounds 1–2 setup contracts, ambiguous task inference, wrong
  protocol keys, double preprocessing/named-array mismatches, mixed-type tables,
  truncated scripts and repeated unsuccessful repairs. Evidence in experiments
  bench/dev-loop/round-01/REVIEW.md and round-02/REVIEW.md, with original attempts.
- Anticipated rails are prospective design choices, not fabricated observed failures.
- Instructions only; no train-index, sandbox, test-lock, scope or evidence check
  is weakened. Six prior review points are addressed in the revised proposal.
- Active set: rails-0.3, 24 instruction rails including unchanged provisional RL-0001.
- The work-order-05 baseline deliberately changes engine, model and rails relative
  to exploratory rounds. No causal comparison with those rounds is claimed.
- Commit: resolve from the activation commit introducing this entry; exact hash
  is added to the next status update. Focused regression results recorded below;
  final baseline full suite runs once at Step 1.7 before any live batch.

Activation gate: 17 focused loader/scope/genericity/setup tests passed in 0.58 s.

## B-0002–B-0005 — work order 05 Step 1.2

- B-0002 / E1: equivalent metric case/aliases normalize before enum validation;
  unsupported metrics still fail. Evidence: Round 1 regression RMSE spelling.
- B-0003 / E2: task_metrics.py is the single primary-metric registry used by
  setup, runner, task review and sub-goal checks; no metric selection changes.
- B-0004 / E3: optional call_deadline_s runs SDK transport in a trusted process
  killed and reaped at the hard deadline. Secret-bearing input uses pipes only.
  Timeout is provider_error and follows existing bounded cooldown recovery.
  Late upstream billing is unavailable, never zero. SDK idle timeout is separate.
  Evidence: Round 1 response exceeded 90 seconds of elapsed time.
- B-0005 / E4: unsupervised brief/action labels no longer request outcomes or
  call a random split stratified. Stable action IDs remain for replay compatibility.
  Each action now has its own procedural methods_text rather than shared boilerplate.
- Regression tests: tests/unit/test_batch_baseline.py; existing setup/inference
  integration regressions. Final full suite is the Step 1.7 gate before live calls.
- Activation commit for L-0002: 5ded618. This group commit hash is linked from
  the next status entry. No scientific safeguard is relaxed.

## B-0006 — work order 05 E5, author-approved setup values and spelling maps

- Every visible column exposes at most twenty distinct values/counts, or numeric
  min/max/mean/quartiles; high-cardinality nonnumeric summaries are unavailable.
  Hidden evaluation columns are removed first. No cross-column raw rows are sent.
- Each setup egress envelope records the exact setup_inventory and its payload
  hash. This is an explicit author-approved expansion beyond schema-only setup.
- Optional target label_map needs a reason and observed source/destination values.
  Only whitespace/case/trailing-period variants may merge. Original inputs are
  unchanged; project-owned projections record mapping, reason and source hash.
  Cardinality validation uses the mapped proposal, never a silently normalized input.
- Evidence: documented label spellings in Adult; four raw categories qualify the
  earlier claim that its multiclass setup was inherently incorrect.
- Tests: setup values/egress/exclusion, map validation, atomic registration and
  source preservation. Final full suite remains Step 1.7.
- Prior engine E1–E4 commit: d48b0f8. This entry's commit is linked next.

## B-0007 / E6 — fitted input columns

fit_record snapshots input column names before estimator.fit and retains them in
manifest fits and StepCompleted. No row values are logged. Legacy unknown column
sets remain unavailable to the external scorer. Full frozen-index enforcement is
unchanged. Evidence: work-order-05 leakage outcome requires explicit fitted inputs.

## B-0008 / E7 — training group metadata

The frozen partitions retain group columns for internal folds; protocol and rails
exclude them from predictors. Group-disjoint outer splitting remains enforced.
Two focused regressions cover value-free fitted-column records and train groups.
E5 prior commit: 9026276. Final full suite remains the Step 1.7 gate.
