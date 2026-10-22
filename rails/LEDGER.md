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

## B-0018–B-0020 — batch-03 engine contract corrections

Evidence: batch-03/REVIEW.md and its curated hashed scripts/logs in the
experiments repository. Seeds KMeans/threadpoolctl reads own-process library
maps; exact read-only /proc/self/maps is allowed by author decision. Other
/proc reads and writes stay blocked; sandbox A is unchanged. A synthetic
KMeans fit through fit_record inside bubblewrap exercises the actual path.

Bike legitimately declares poisson_deviance but action text requests rmse,
repeating batch-02 Covertype's roc_auc versus roc_auc_ovr mismatch. All twelve
validation/test actions across six templates now name the nested declared
metric. Primary checks are unchanged. One scoring-only retry (bounded to one
completed scoring attempt) stays within validation; exhausted scoring cannot
automatically select an upstream loop. No training/test gate is weakened.

Optional reasoning_effort is transported and logged with requests; None keeps
existing behavior. Controller records the setting and requires it to match for
ablation. Batch 04 leaves it unset; batch 05 will isolate explicit low effort.
No captured error values, reference code, model change or silent historical
rescoring. Focused contracts/sandbox:44 passed; final full gate follows.

## L-0005 — batch-03 instruction revisions (rails-0.6)

RL-0004: consecutive periods of one series require time columns regardless of
stated prediction aim; do not substitute seasonal encodings for chronology.
Bike's temporal requirement is retained by author decision.
RL-0018: categorical multi-output metrics operate on each target then average;
subset accuracy is an exact row-wise comparison, never an unsupported matrix
metric call. Anuran still failed after the previous instruction.
RL-0022: PCA uses inverse_transform(transform(X)), not predict; MLP reconstructor
uses predict and its middle hidden layer supplies embeddings. Optical Digits
failed validation by calling predict on its PCA Pipeline.

No new rail or hard-coded dataset/column. All26 active rails remain instructions.
Source fixes B-0018–20 are separate. Batch04 model settings remain unchanged;
output budget intervention is reserved for setting-only batch05. Before/after
results are pending; no rail effect is inferred from wording tests.

### B-0020 compatibility follow-up before batch 04

Review found unguided native sessions did not receive _protocol. All action
input resolution now supplies the same immutable protocol snapshot, filling
a missing task metric from the existing registry without changing recorded
state or an explicit override. This keeps the new instructions usable on
older native projects. The first partial gate was deliberately interrupted
before this source change; its exit2 logs are retained as superseded.

The final guided-driver recovery uses the same bounded scoring rule as CLI
options, skips an unnecessary Navigator call, and suppresses upstream loop
cards while the primary metric is missing. A dedicated synthetic turn test
proves that only validation scoring is recommended, then exhaustion stops with
a gate refusal. Review caught duplicate validation/test methods text; each
action now has a distinct report description. Earlier partial gate logs are
superseded, not a completed suite.

## B-0021 — enforce joint grouping and chronology (batch04)

Evidence experiments4a380e1, Bike SplitFrozen and external leakage-score.json:
correct date/hour declarations were silently overridden by a day group, causing
time_ordered=false. Joint group_time splitting now merges overlapping group
intervals (including equal timestamps) into indivisible chronological components
and chooses boundaries closest to requested row fractions without dropping rows.
If fewer than three components exist, refuse clearly rather than reverting to
random grouping or separating an entity. Existing group-only/time-only paths
are retained. New freeze and partition regressions use only synthetic rows,
including overlaps, ties, missing columns and impossible constraints.

## B-0022 — make Navigator question/goal contracts explicit (batch05)

Evidence experiments9447df6, Retail Navigator responses01M526MZAA2THCD3QCFEDSX3RQ
and01M526N6TG21Y3RE0HY2Y3VTYP. BOTH recommended build_entities. First advanced
an invalid prefixed goal; repair corrected that but still invented returns_rule
parameters and omitted effect.kind. Strict validation rejected the scene, then
the fallback policy recommended distribution-only EDA. Do not blame the model
for deliberately selecting that action or attribute the failure to word limits.

Current local goal IDs, action parameter schemas/contracts and executable
question-effect examples are now supplied. Instructions require supported kind
and fields, declared parameters only, and pause for an unrepresentable essential
scientific choice. No question is ignored and no undeclared mutation accepted.
Synthetic scripted Navigator and negative-effect regressions preserve refusals.

## B-0023 — reconstruction output contracts and value-free hints (batch05)

Digits validation repaired predict-on-PCA and inverse_transform-on-MLP, then
computed its metrics but crashed creating an UNDECLARED validation embedding
file without explicit row_id/partition. Validation now requests metric summaries
only; test alone requests the declared per-row embedding artifact. Candidate
interfaces and fitted frontend space are explicit. Fixed diagnostics explain
known interface errors and schema errors without forwarding captured values.
No training index, output population, test lock or privacy rule is relaxed.
Fifteen focused library/API/split/rail tests passed; full gate follows.

## L-0006 — representation interfaces and declared row outputs (rails-0.7)

Evidence batch05 Digits three validation attempts, experiments9447df6. Refine
existing RL-0022: use the fitted frontend once and the appropriate final decoder;
MLP does not invert a pipeline. Metric-only validation creates no embedding
file; declared per-row outputs need row_id and partition columns, not an index.
All26 rails remain instructions. No dataset/model/column-specific instruction,
reference implementation, hidden-label tuning or new scientific rule.
Source contracts B-0021–23 remain a separate commit. Low reasoning effort and
all other generation settings remain fixed in the next source-revision batch.

## B-0024 — prepared table preserves declared constraint columns (batch06)

Retail preparation executed but renamed the declared group to entity_id and
omitted its declared time column. The joint splitter correctly refused. The
action contract now requires exact declared names as complete explicit columns;
any entity-level temporal aggregation must be documented and consistent.
Collection validates these fields and unique/nonempty row IDs before marking
the step complete, so the existing bounded Worker repair can fix the artifact.
No group/time constraint is dropped or renamed implicitly. Six synthetic
collection cases cover renamed/missing/null fields, empty/duplicate index and
the correct artifact. No original failed script is patched or rerun.

## B-0025 — value-free diagnostic for an expected array returning None

Digits passed validation but private sklearn ACTIVATIONS returned None in its
test embedding code. Fixed diagnostics explain missing returns/in-place
functions without sending captured data. The actual numeric API is exercised
with a tiny synthetic MLP: public activation propagation reaches the true
middle bottleneck with a finite 2D result. This is a regression fixture, never
a no-AI research arm or a replacement for Worker analysis code.

## B-0026 — compact private fingerprint cache, unchanged matching policy

Measured Covertype cache reached45GB while free disk is39GB, blocking repeated
full-size acceptance. New stores use normalized v3 dictionaries for dataset
names,column names and identical salted value digests, with integer cell
references and indexed v2-compatible cells/rows views. Both precisions4/6,
row HMACs, distinct-cell threshold and matching algorithms are unchanged.
Value-ID cache is bounded65536; tests exercise eviction with limit8.
Historicalv2 is read/written unchanged, never silently migrated. v1 rebuild
remains atomic from hash-verified sources; failed migration preserves bytes.

An outside-source prototype was tested while batch06 ran, without changing
active code or using real benchmark data. Synthetic store13.15MB became1.66MB;
identical cells/full-row hashes and verdicts, including legacy read/write.
17 existing synthetic privacy tests passed on prototype, excluding two schema
fixtures for adaptation. Those are now adapted and included:29 focused
cache/migration/schema/MCP/privacy/preparation tests pass45.63s. Full gate
follows before any live run. No claim of actual large-cache savings yet.
Private archives, salts and scientific artifacts are preserved.

## L-0007 — preparation metadata, analysis units and actual embeddings (rails-0.8)

Evidence batch06, experiments ef3d703. Refine existing rails only:
RL0004: group/time constraints describe final analysis units; raw event dates
used only for static aggregation do not automatically imply temporal cohorts.
Consecutive periods of one series still require chronology.
RL0020: entity artifacts retain declared group/time names as complete columns,
not an arbitrary entity_id or index; temporal aggregation is explicit.
RL0022: private ACTIVATIONS mutate in place/returnNone; public activation
results propagate to the actual bottleneck, returning finite2D train/test
arrays of the same width. No training on evaluation rows or labels.
All26 rails remain instructions, no dataset/column/model-specific rule.
Low effort and all other generation settings stay fixed for batch07.

## L-0008 — entity segmentation setup constraints: static clustering requires no time split (rails-0.9)

Evidence batch07, experiments 9be8c34. Optical Digits qualified end-to-end.
Online Retail completed all 12 steps to report and passed all three leakage
criteria (fitted columns, disjoint groups, time ordered), but recorded setup
disagreement on time_columns because Navigator listed InvoiceDate during onboard.
Under the author's prospective decision, static customer segmentation does not
require chronological splitting (manifest time_columns is empty).
Refine existing rail RL-0004 only:
- RL-0004: When clustering or segmenting static entities from transactional
  records, leave time_columns empty ([]); transaction timestamps used only to
  aggregate static features (such as recency relative to an observation date)
  are not time columns for partitioning. Consecutive periods of a single series
  still require chronology.
All 26 rails remain instructions; no table, column, model, or dataset identifier is named.
Low reasoning effort and all other settings remain fixed for batch08.


## B-0027 — empty nested alternatives in the setup proposal are dropped

Evidence: first acceptance batch (direct `deepseek-flash`, experiments `b5c56d8`,
`bench/comparison/acceptance/`). Heart run 1 and Optical Digits run 1 returned
`"alternatives": []` inside an alternative; the schema forbids the key, the one
JSON repair repeated it, and Heart stopped at setup (Digits recovered on repair).
`Inference` now drops an empty or null nested `alternatives` before validation.
It carries no content. Non-empty nesting is still refused. Test:
`test_empty_nested_alternatives_are_dropped_but_content_stays_invalid`.

## B-0028 — over-long display text is clipped, not a reason to reject a decision

Evidence: same batch. Online Retail runs 2 and 3: the Navigator recommended
`build_entities`, but `what_happens` (or `situation`) exceeded its character or
word limit in both the reply and its repair. The engine fell back to the template
default, the eda event ended without entity rows, and the group split refused
missing customer keys. Display fields (`title` 80 chars/8 words, `why_now` 200,
`what_happens` 200/20 words, `situation` 240) are now shortened deterministically.
Decision fields (action, parameters, recommendation, question effects) stay
strictly validated. Test: `test_long_display_text_is_clipped_not_rejected`.

## B-0029 — time split boundaries move to the nearest timestamp change

Evidence: same batch. Bike Sharing runs 1 and 2 declared a date column only;
24 rows share each value, the fixed 60/20/20 cut points fell inside a date, and
the built-in split refused with no repair path. When the exact fractions would
separate equal timestamps, each boundary now moves to the nearest change of
timestamp; equal timestamps never span partitions, and the counts are recorded
as before. Tables without ties keep the exact earlier split. Fewer than three
distinct timestamps still refuses. Tests: three `test_time_split_*` cases.

## B-0030 — fit_record refuses target, excluded and group columns as inputs

Evidence: same batch. Energy Efficiency run 3 fitted the alternative model
with both targets in X (later steps failed on them); Anuran Calls run 3 fitted
a feature transformer on a frame containing the three targets and the group key
(external leakage check failed). The engine recorded these fits but did not stop
them. `fit_record` now refuses any fit whose input columns include a declared
target, an excluded column or the group column, with an `MLCA:` message the
Worker can repair in the same step. Survival duration and event columns are
exempt (Cox models read them from X). Group values still reach folds through
`groups=`. Tests: `test_fit_record_refuses_protected_columns`,
`test_protected_columns_cover_outcomes_exclusions_and_group_except_survival_fields`.

## B-0031 — setup failures keep the engine message

Evidence: same batch. Optical Digits run 1 failed after a valid setup proposal
with only "Setup failed: MlcaUserError"; the cause could not be read. Its time
falls in the batch's disk-full interval, so it is classified as infrastructure,
probable, not confirmed. Engine refusals (value-free by design) now keep their
first line, at most 300 characters. Test: `test_setup_failure_keeps_engine_message`.

## L-0009 — joint outcome levels, datetime columns, no target encoders (rails-0.10)

Evidence: same batch. Refine existing rails only:
- RL-0002: categorical outcome columns at nested levels (each coarser level
  determined by a finer one) are joint outcomes; do not keep only the finest
  level and list the others as leakage suspects. Anuran Calls runs 1 and 2 kept
  one level and excluded the others, disagreeing with the declared task.
  Single-table evidence.
- RL-0003: joint outcome columns are targets, not leakage suspects of each other
  (removes the conflict between RL-0002 and RL-0003).
- RL-0010: columns already of datetime type become numeric parts or days since a
  fixed reference date; never pass them to imputers, scalers or encoders. Online
  Retail run 1 passed a datetime column to an imputer in all three attempts.
- RL-0018: target encoders removed; consistent with B-0030.
All 26 rails remain instructions; no table, column or model is named.

Not changed: the three Covertype runs (disk exhaustion at setup in runs 1 and 2;
the 90-minute deadline at the model step in run 3 on a 4-CPU host running four
studies). These are infrastructure outcomes; acceptance needs a host with enough
cores per study. Next: rerun the failed tables, then a fresh 12 x 3 acceptance on
one model route, unchanged version.

## L-0010 — remaining development failures (rails-0.11)

Evidence: first acceptance batch (rails-0.9) and batch-09 (rails-0.10). Generic
corrections; no table, column or model is named:
- RL-0010 now also applies at eda, features and model, and covers date columns
  created in earlier steps. Online Retail batch-09 passed first and last invoice
  dates from entity aggregation to the clustering model (step 7); RL-0010 had
  applied only at preprocess.
- RL-0017: when the evaluated partition lacks some model classes, compute the
  macro one-vs-rest value as the mean of binary per-class AUCs; never pass a column
  subset of the probability matrix. Anuran Calls acceptance run 1 (step 10, all
  three attempts) passed predict_proba columns for the classes present in the
  validation rows only, so rows no longer summed to 1. Single-table evidence.
- RL-0027 (new): saved transformers that both expect the raw feature columns are
  alternatives, never chained. Optical Digits batch-09 (step 8) chained a saved
  preprocessor and a saved selector, both fitted on raw columns.
Already covered, no change: Energy run 3 and Anuran run 3 (targets in inputs,
B-0030); Heart run 1 (B-0027); Bike runs 1-2 (B-0029); Online Retail runs 2-3
(group split on transactions with missing keys after the fallback skipped entity
building, B-0028; RL-0020 drops rows without an entity key); Covertype and Optical
Digits run 1 (infrastructure). 27 rails, all instructions. Next: fresh 12 x 3
acceptance on rails-0.11.

## B-0032 — saved preprocessing and models accept the raw columns

Evidence: acceptance-02 (rails-0.11). Bike Sharing runs 2 and 3 derived date parts in
a temporary frame and fitted the saved preprocessor on them (step 5); later steps
loaded the raw partition and failed on the missing derived columns (steps 6 and 7).
RL-0026 already asked for derivations inside the saved pipeline. `save_model` now
refuses, in the preprocess and model events, an object whose `feature_names_in_`
are not columns of the frozen training partition (MLCA: message, same attempt).
Selectors in the features event may still follow saved preprocessing (RL-0011).
Test: `test_saved_objects_must_accept_raw_columns`.

## B-0033 — interpretation reads at most 10000 rows per partition

Evidence: acceptance-02. Covertype run 1 ran permutation importance on 116k
validation rows with 20 repeats and passed the study deadline at step 11; RL-0015
asked for subsampling. Interpretation actions fit nothing; their train and val
inputs are now a fixed-seed sample of at most 10000 rows, in original order, when
a partition is larger, and the work order says so. Test:
`test_interpretation_reads_a_fixed_ordered_sample_of_large_partitions`.

## B-0034 — disk exhaustion is recorded, and prevented by the controller

Evidence: acceptance-02. Covertype run 3, Online Retail run 3 ("Setup failed:
OperationalError") and Seeds run 1 (no run record) failed when free disk fell to
86 MB and 11 MB (`resources.jsonl`), not from SQLite locking. A Covertype project's
private row-fingerprint store is 4.3 GB. Setup failures now keep SQLite messages and
OS error names. The batch controller (mlcagent-experiments) waits for free disk
before starting a study and removes `.mlca/private` and `.mlca/env`, never
published, once a study is scored. The output allowance becomes a plan parameter,
default 32768: Adult run 3, Covertype run 2 and Bike Sharing run 1 spent all 16384
output tokens on reasoning. Test: `test_setup_reason_keeps_database_and_disk_causes`.

## L-0011 — binary recodings and the saved model contract (rails-0.12)

Evidence: acceptance-02.
- RL-0002: the joint-outcome rule (rails-0.10) applies to hierarchies of named
  categories. A binary column that thresholds an ordinal grade is the outcome; the
  grade is a leakage suspect (RL-0003). Heart Disease runs 2 and 3 modelled the grade
  and its binary recoding together as multilabel, disagreeing with the declared task.
- RL-0011: states the B-0032 contract for later steps. Dry Bean run 1 (step 11)
  refused a saved model because it was not a Pipeline, though it accepted the raw
  columns; the failure was in the generated check, not in SHAP.
27 rails, all instructions. The setup scorer is unchanged. Next: fresh 12 x 3
acceptance on rails-0.12.

## B-0035 — saved objects keep the row index on later rows

Evidence: batch-10 (rails-0.12). Bike Sharing (step 7) failed in `predict` on
validation rows: a date branch built from NumPy functions inside a pandas-output
ColumnTransformer dropped the row index. Fitting on training rows indexed from 0
hid this in step 5. In the preprocess and model events, `save_model` now applies
the object to the last 200 training rows and refuses it, with an MLCA: message in
the same attempt, if it fails or returns rows that do not match its input rows.
Test: `test_saved_objects_must_keep_the_row_index_on_later_rows`.

## L-0012 — clustering versus representation (rails-0.13)

Evidence: batch-10. Seeds proposed representation for seven distinct kernel
measurements, disagreeing with the declared task. RL-0002: representation is for
channels of one signal (pixels, spectra, sensor readings); a few distinct measured
attributes of entities mean clustering. Seeds remains accepted from acceptance-02
under pooled acceptance. 27 rails, all instructions. Next: Bike Sharing, 3 runs on
rails-0.13.

## B-0036 — external cohorts sealed in autonomous runs

Pre-freeze support for the biomedical studies (S3, S4), not caused by a run failure.
`mlca run --external FILE` (and `runner.run(external=...)`) registers each external
cohort with role `external`: setup inference sees only the study tables, the
Navigator's state view omits the external table's schema, and the engine opens the
cohort only after the test unlock. Before this, an external table in the study folder
would have been registered as discovery data. Tests: `tests/unit/test_bio_readiness.py`.

## B-0037 — the test step saves per-row predictions

Pre-freeze support for the AutoML comparison: acceptance-02 saved no per-row test
predictions (the optional `audit_test` action was never chosen), so paired per-row
tests against AutoML were impossible. In the classification and regression templates,
`score_test` now also saves `test_predictions.parquet` (row_id, partition, y_true,
y_pred and proba__<class> in the model's class order; no feature columns) as a
required output. Templates changed; rails unchanged (rails-0.13).


## B-0038 — E-W1: bounded model-facing wide schemas (reopening-v2)

Evidence: eval-01/EVALUATION_SUMMARY.md, Failure causes, and the setup egress
byte counts under ../mlcagent-experiments/bio-bench/runs/deepseek-flash/eval-01/.
HTTP 400 response bodies were unavailable; the oversized contexts are observed,
while their causal relationship to the rejection remains an inference.

For tables wider than 200 columns, setup retains nonnumeric, low-cardinality,
brief-named and first/last 20 fields. Remaining numeric fields are aggregated by
dtype with count, missingness and ranges of minima/maxima/means. Full local tables
still validate proposals. Registered inventories retain local summary statistics;
Navigator views, Worker briefs and structured prompt contexts abbreviate wide
collections with explicit omission counts. Repair retains that bounded work order.
No rows are sampled by the controller and no execution schema is truncated.

Tests: tests/unit/test_wide_schema.py (25,000 numeric features plus two labels;
model contexts for all template events, repair, and actual stubbed setup request
with matching egress bytes), existing inference and Worker contracts. The 200 kB
assertion covers the specified synthetic requests; a table with thousands of
mandatory low-cardinality/nonnumeric fields or a huge user brief can still exceed
it. Those fields are not silently dropped. Changes: schema_summary.py, inventory,
state_view and prompt construction. Commit: E-W1: bound wide-table model contexts.


## B-0039 — E-W2: retain bounded provider rejection details

Evidence: eval-01/EVALUATION_SUMMARY.md: 21 HTTP 400 setup failures have status
codes but no provider explanation. New HTTP failures extract only error.type
(or code) and error.message, redact configured credentials, and truncate each to
500 characters in usage and ProviderFailed. Full response bodies, request objects
and headers are not added. Both direct SDK errors and deadline subprocess errors
retain these fields; absent diagnostics stay absent. Original eval-01 is unchanged.
Tests: test_provider_error_details.py; DeepSeek/provider-resilience regressions,
17 passed. Files: llm/provider_errors.py, client.py, request_worker.py and the
compatible adapter. Commit: E-W2: retain redacted provider rejection diagnostics.


## B-0040 — E-M1: exact primary metric in scoring-only recovery

Evidence: eval-01/EVALUATION_SUMMARY.md; two validation runs recorded only
per-model names, leaving the exact primary-metric check unsatisfied. The existing
single scoring-only retry now tells the Worker the selected model's exact key and
val split, with the required record_metric call. Per-model names are explicitly
additional and cannot satisfy the check. No fitting is reopened or metric inferred
from per-model values. Tests: test_metric_recovery_key.py and existing scoring
recovery regressions, 19 passed. Commit: E-M1: name the exact metric in validation recovery.


## B-0041 — E-S1: retain survival outcome fields through preparation

Evidence: eval-01/studies/s4_hnscc-003/attempt-001/run-001/.mlca/log/events.jsonl
in ../mlcagent-experiments/bio-bench/runs/deepseek-flash/. BriefRecorded resolves
both outcome fields, InferenceRecorded additionally calls duration a leakage
suspect, and TaskConfigured excludes it because only targets were protected.
DataPrepared/SplitFrozen precede the training-review refusal. No table was opened.

This is an engine distinction: an outcome must not become a predictor, but it must
remain in the partition for scoring and train-only review. Autonomous exclusions
now protect duration/event, and preparation retains both even when an older setup
marks them excluded. Existing runtime predictor guards remain authoritative. No
survival rail, Worker fix or survival development run is added. Three synthetic
regressions cover setup, preparation/split/train-only reads and missing-event
errors; surrounding review/readiness tests also pass. Commit: E-S1: retain survival outcomes in frozen partitions.


## L-0013 — RL-0028: primary validation metric (rails-0.14)

Observed evidence: eval-01/EVALUATION_SUMMARY.md, two validation-scoring stops
with per-model metric names but no selected-model primary key. The generic
validation-only instruction requests the exact protocol key, in addition to
per-model values, using existing fitted objects. E-M1 supplies the exact call on
recovery. No model family, dataset name or column name is prescribed. Survival is
explicitly outside this new rail's problem scopes. The other 27 rails and all
scientific/sandbox checks remain unchanged. Tests: test_metric_recovery_key.py,
loader/snapshot and genericity regressions. Commit: Rails: add exact validation metric rail 0.14.


## L-0014 — RL-0029: bounded wide interpretation (rails-0.15)

Observed evidence: ../mlcagent-experiments/bench/dev-loop-v2/batch-01/REPORT.md
and these development-run records (model: deepseek-flash; category: timeout):
- studies/gli85_glioma-001/attempt-001/run-001/.mlca/steps/11_interpret_explain_model_EQSSWR93/
- studies/gcm_tumour_types-001/attempt-001/run-001/.mlca/steps/11_interpret_explain_model_ZHCT2RJ0/

Both step paths are relative to ../mlcagent-experiments/bench/dev-loop-v2/batch-01/.
All three scripts per step attempt full-width permutation over approximately
16,000–22,000 input columns, with 20 repeats. The event logs record interpretation
timeouts (GLI-85 attempts 1 and 3; GCM attempts 1, 2 and 3). Historical scripts,
outcomes and input tables are not modified or rerun.

The new Worker interpretation instruction applies only to non-survival tasks.
Above 500 input features, use the frozen model's own coefficients/importances,
or permute only its top 50 ranked features with at most 5 repeats. Retain the
complete prediction schema, never refit, record the method and budget, and report
an unavailable ranking rather than reverting to full-width permutation. Stay
within the existing step timeout. This is an instruction, not a new runtime cap
or a guarantee that model-written scripts obey it or finish in time.

The classification action contract visible to the Navigator and Worker previously
requested 20 repeats unconditionally. It now keeps that budget only for at most
500 features and states the same wide-input limit; its methods text allows native
importance as well as permutation. No Navigator code sets a separate budget.
Other action contracts, earlier rails, row sampling, fit/test safeguards and
sandbox timeouts are unchanged. No dataset names or column names enter the rail.

Tests: tests/unit/test_wide_interpretation_rail.py checks all seven non-survival
problem scopes, Worker prompt and repair propagation, and the Navigator-visible
classification budget. Loader/snapshot, genericity and bounded-context regressions
are checked separately. Commit: Rails: bound wide interpretation (rails-0.15).

Offline verification: 48 focused tests passed, including the genericity test;
Ruff and whitespace checks passed. The full suite and live batches were not run.
