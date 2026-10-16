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

## B-0009 — shared batch controls and explicit ablation

Work order 05 Step 1.6: explicitly configured shared request pacing across isolated
process configuration directories; unset spending ceilings remain unlimited, not
unknown-price refusals. Unknown usage is still unavailable, never fabricated as
zero. rails_enabled=false snapshots rails-0.0 for the specified ablation only.
Default native configuration stays unchanged. Twelve focused tests passed.
E6/E7 implementation: bf8814b; researcher-only manifest fields: 99b415b.

## B-0010 — optional deadline transport compatibility (baseline gate)

The first Step 1.7 suite found 18 failures: SDK adapter test doubles constructed
without __init__ had no config attribute. The optional deadline now defaults to
legacy synchronous transport only when absent. Real configured deadlines still
use the bounded subprocess; a new positive dispatch test proves that path.
No engine safeguard is bypassed. The affected accounting/refusal/truncation and
new baseline tests then passed: 44 passed in 27.68 s. The complete suite then passed in four isolated offline test processes:
408 passed, 1 skipped, zero failures/errors. Experiments: 18 passed.
Controller Step 1.6 commit: eb70bd3. No live call occurred before the gate.

## B-0011 — explicit setup wire proposals (batch-01)

Evidence: experiments d792b50, batch-01 Adult, Dry Bean and Abalone setup
responses omit targets even while naming an outcome in their reason. Successful
proposals omit defaulted grouping/time/leakage fields as well. The provider JSON
schema now requires explicit values (including null/empty) for every proposal
field; context-bound inference validation enforces that contract during bounded
repair. Historical decoding keeps its defaults. The scripted setup response
helper now emits the complete published response; no invalid case is removed.

## B-0012 — bounded-memory privacy matching (batch-01)

Covertype audit completed in 1.918 s but collection built common-value matches
until an implementing-agent infrastructure stop at 1514 s total, RSS 5,762,836
KiB. Evidence: batch-01/covertype-infrastructure-intervention.json and raw log.
A bounded existence preflight rejects impossible matches. Eligible matches merge
row-ordered cursors and retain only one source row's bipartite graph. The three
cell threshold, name-independent matching and both precisions are unchanged.
Tests compare the previous algorithm on randomized synthetic cases and verify
common-value short-circuiting, duplicate-cell rules, renaming and rounding.

## B-0013 — actionable value-free refusals (batch-01)

Retail supplied an event name as a metric partition and repeated it after an
opaque refusal. The runtime now names the allowed partitions and recommends
sourced facts for pre-split counts, using MLCA-prefixed value-free messages.
Existing split/test rules are unchanged. Fixed diagnostic hints explain sklearn
set_output incompatibility (Heart), missing __main__ definitions in saved
objects (Energy/Anuran), and renamed columns (Optical). No captured library
message values are sent. Canary tests prove values remain local.

Focused engine/legacy guard regressions: 22 passed in 0.96 s. All source changes
are between batches. No hand-written analysis or current-study script changes.

## L-0003 — batch-01 consolidated instruction repairs (rails-0.4)

- Cause/evidence: experiments d792b50, curated batch-01 step scripts, diagnostics,
  request envelopes and REVIEW.md. Engine corrections B-0011–B-0013 are separate
  (c2b9978); no model/generation setting changes in this instruction revision.
- RL-0008: numeric correlation only for numeric outcomes (Anuran string-outcome
  conversion failure). Exact derivation checks and warning-only correlation stay.
- RL-0009: named output requires compatible components (Heart set_output error).
- RL-0011: inspect fitted feature names and apply the saved frontend only once
  (Optical transformed columns into a raw-column pipeline).
- New RL-0025: persist importable package objects rather than local __main__
  definitions (Energy/Anuran cross-script unpickling failures). No dummy behavior.
- All wording is generic. No dataset/column/model identifier appears in the rails.
- Output-budget failures remain recorded. Hidden reasoning is not controlled by
  a shorter visible-script instruction; explicit effort changes, if needed,
  belong at a recorded batch boundary with model/rails changes separated.

## B-0014 — per-row audit artifacts match the runtime (batch-02)

Evidence: experiments 4a9a60d, Breast validation audit, Dry Bean test audit and
Covertype supporting validation audit. Actions required CSV row outputs while
the runtime requires local Parquet, row_id and a train/val/test partition. Align
all shipped prediction-audit output specs to data-kind Parquet and spell out
the helper schema in Worker write/repair orders. Unsupervised audits use only
cluster assignments or embeddings, never outcomes. No row egress, privacy,
partition or fitting validation is relaxed. Frozen historical projects retain
their snapshotted templates; only new projects use the corrected contract.

## B-0015 — classification action metric agrees with task (batch-02)

Covertype score_validation attempt2 ran successfully after a frontend repair,
but its action explicitly requested roc_auc while the task and engine check
correctly require roc_auc_ovr. Audit then failed under B-0014. Validation, test
and interpretation instructions/methods now distinguish binary and multiclass
scoring, use the declared primary metric and forbid binary thresholds for
multiclass. Legacy AUC fact keys are used only for corresponding AUC values.
Distinct metric names stay distinct; checks are not weakened to accept them.

## B-0016 — fixed, value-free scoring repair hints (batch-02)

Adult repeatedly supplied unsupported roc_auc_score(pos_label=...). Anuran
used a whole multiclass-multioutput target matrix, mixed encoded/predicted label
types, then attempted fitting during validation. Fixed diagnostic hints explain
probability alignment, per-output categorical scoring and reuse of training-only
encoders. No captured error values or labels leave the machine. Fit refusals
remain enforced. Focused new/legacy Worker and contract regressions:40 passed
in1.70s; the full gate follows consolidated rail changes before another batch.

## L-0004 — batch-02 consolidated instruction repairs (rails-0.5)

Evidence: experiments4a9a60d, batch-02 curated step scripts and request envelopes.
Engine/template contracts B-0014–B-0016 are separate (43b7407). Model and
reasoning/output settings remain unchanged for this instruction revision.
- RL-0017: Adult's unsupported AUC pos_label argument; align a binary indicator
  and probability column while preserving labels for other metrics.
- RL-0018: Anuran's unsupported matrix metric, mixed label types and attempted
  validation-time encoder fitting; evaluate per output and reuse training mappings.
- RL-0020 now reaches Navigator as well as Worker: Retail chose distribution-only
  EDA and never selected its existing build_entities preparation action. Its raw
  missing entity keys correctly blocked the group split. Recommend preparation
  before EDA completes, retaining the existing prepared-data and fit contracts.
  The author still decides the external static-versus-temporal criterion.
- RL-0026: Bike's saved frontend depended on transient date-derived columns;
  preserve all feature derivations inside the reusable training-fitted pipeline.

No dataset, column or provider/model identifier appears in rail text. No
sampling, altered target, leaked manifest answer or relaxed engine safeguard.
Output-budget failures remain measured; no reasoning-setting change yet.

Focused rail/genericity/metric-contract regressions:34 passed in2.49s.
The full consolidated native suite is required before the next live batch.

## B-0017 — explicit frozen populations for local row outputs (batch-02 follow-up)

Before another live call, source inspection found the collector historically
requires train+test rows for every test data artifact (originally only clustering/
representation outputs). New test prediction audits correctly need test rows
only. OutputSpec now permits a trusted, nonempty unique row_partitions contract
for data-kind Parquet, with test access still required. The collector compares
the exact declared frozen membership, checks unique/nonmissing IDs, and marks
data artifacts local-only. Validation audits require val, test audits test;
unsupervised evaluation still requires train+test. Historical test data without
an explicit contract retains train+test, verified by a negative regression.
Malformed output contracts are refused by the template loader. No scientific
population, test lock, privacy or fit validation is weakened.

The first batch03 full gate was deliberately interrupted before source changes;
its four exit2 logs are retained as superseded, not reported as a passing gate.
Forty-two focused template/runtime/collector/metric/rail tests passed in2.97s.
A fresh full gate follows the final contract; no live batch03 call occurred.
