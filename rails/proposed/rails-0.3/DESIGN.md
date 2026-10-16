# rails-0.3: design pass for all 12 development tasks (proposed, not active)

Written 16 October 2026 by Claude Code at the author's request. **Status: proposed.** The files here
are not loaded by MLCA: the loader reads only `rails/*.yaml`, so this subfolder does not affect
round 2 or any project created before activation. The execution agent activates and tests the
set; the author reviews the rails at the end of development.

## Why a design pass

Rounds 1–2 found failures one table at a time (round 1: 0/12 past setup; round 2: three tables
stopped, at setup contracts, saved-pipeline chaining, a summary table and truncated output). Most
of the failures that remain are predictable from the 12 task types, so this set writes the generic
rails for all of them at once. Later rounds then repair only what the set did not anticipate.

Rules followed:
- Generic: no dataset ID, file name or development column name in any rail text or reason. Checked
  with the same rule as `tests/unit/test_rails_generic.py` (0 violations).
- Written from development evidence and the 12 task types only. No held-out file was opened. The
  designer knew the held-out list from dataset selection; no rail targets a held-out property.
- Instructions only. Existing engine rules (sandbox, `fit_record` on the full frozen training index,
  test lock, excluded columns) stay authoritative; no rail relaxes them.
- Short: per request the matching rails add about 260 words to Navigator setup and 290–670 words to
  a Worker script request (at most about 730 words).
- `RL-0001` is kept unchanged and stays provisional (STUDY_DESIGN §3, development procedure 6).

Static check done: `mlca.rails.load()` accepts the folder (rails-0.3, 24 rails, digest
`b17cfac3eff9…`), plus the genericity rule. **No behavioural test was run**; that is the execution
agent's job.

## The rails

`O` = observed in rounds 1–2 (evidence in `../mlcagent-experiments/bench/dev-loop/`); `A` = anticipated
from the task types.

| Rail | Role · events · problems | Rule | Basis |
|---|---|---|---|
| RL-0001 | navigator · onboard · all | One concise setup proposal; alternatives only for real ambiguity | O (round 1, truncated setup) |
| RL-0002 | navigator · onboard · all | Problem type from outcome cardinality and type; multilabel when several categorical outcomes describe one row; clustering vs representation when no outcome | O (round 1: binary proposed as multiclass, multi-output as one target) |
| RL-0003 | navigator · onboard · all | Leakage suspects (parts, sums, recodings of the target; post-outcome) and identifier suspects | A (raw-score source of a binary target; component counts) |
| RL-0004 | navigator · onboard · all | Group column for repeated source units; time columns when predicting later periods | A (repeated recordings; hourly series) |
| RL-0005 | navigator · model, validate · all | One scored baseline, at most one alternative, then freeze | A (cost and time per run) |
| RL-0006 | worker · all · all | Read `_protocol` keys; the Brief is a different object; no guessed nesting | O (round 2: `KeyError: 'answers'`) |
| RL-0007 | worker · data→interpret · all | One feature list: all columns minus targets, exclusions, group and key-like columns (text codes, distinct integer sequences); continuous measurements never count as identifiers | A |
| RL-0008 | worker · preprocess · all | Leakage screen on training rows: exclude only confirmed derivations (equality, exact row sum of up to 3 columns); \|r\| ≥ 0.98 is a printed warning only | A (components summing to the target) |
| RL-0009 | worker · preprocess, features, model · all | Keep names: pandas output when the encoding is ≤ 300 columns; otherwise sparse inside one pipeline from the raw DataFrame | O (round 2: arrays into name-based transformer) |
| RL-0010 | worker · preprocess · all | Column typing: one-hot only low cardinality; codes dropped or frequency-encoded; dates parsed to parts | A (invoice codes, date strings, large tables) |
| RL-0011 | worker · features→interpret · all | Inspect saved pipelines before chaining; never apply preprocessing twice | O (round 2: 2 tables, 6 attempts, same fault) |
| RL-0012 | worker · all · all | One type per summary column (NaN, not `''`); ≤ 50 × 12 | O (round 2: EDA table not savable) |
| RL-0013 | worker · all · all | Scripts about 120 lines or fewer | O (round 2: Worker output truncated) |
| RL-0014 | worker · all · all | Minimal repairs from the (sanitised) error type and message; observed messages decoded; `MLCA:` messages are engine rules | O (round 2: three repairs repeated the fault) |
| RL-0015 | worker · all · all | Over 100,000 rows: no quadratic methods; diagnostics on ≤ 10,000-row subsamples; fits on all training rows | A (two tables over 500,000 rows; `fit_record` rejects subsets) |
| RL-0016 | worker · model, validate · all | Tuning only in one `fit_record` call with a search object; `GroupKFold` with `groups=`; `TimeSeriesSplit` only if rows are already in time order | A |
| RL-0017 | worker · model, validate, test · binary, multiclass | Probability column alignment for AUC; `class_weight` under 10% | A |
| RL-0018 | worker · model→interpret · multilabel | `MultiOutputClassifier`, per-target macro F1, mean as headline | A |
| RL-0019 | worker · model→interpret · regression, multioutput | Original scale; Poisson or log1p for counts; target order; per-target and mean | A (count outcome, two-target table) |
| RL-0020 | worker · eda · clustering | Transactions to one row per entity in the entity-building step, before the split; reversing rows by explicit rule | A (transaction table) |
| RL-0021 | worker · preprocess→interpret · clustering | No label; internal criteria; scaled; silhouette `sample_size` ≤ 10,000; per-row clusters | A (classification wording in the cloned template) |
| RL-0022 | worker · preprocess→interpret · representation | No label; scaled reconstruction error; MLP autoencoder embedding without refitting; per-row embeddings | A |
| RL-0023 | worker · data, eda, preprocess · all | Placeholder tokens (`?`, `NA`, whitespace) to missing inside fitted preprocessing | A (`?` in three columns of one table) |
| RL-0024 | worker · preprocess · clustering, representation | log1p for heavy-tailed non-negative features inside fitted preprocessing | A |

## Coverage of the 12 tables (researcher-side; never given to the agent)

| # | Table | Task | Main traps | Rails that address them |
|---|---|---|---|---|
| 1 | Breast Cancer | binary | identifier column; saved-pipeline chain | 0003, 0007, 0009, 0011, 0017 |
| 2 | Heart | binary | target derived from a raw score (`num`); small n | 0003, 0011, 0017 |
| 3 | Adult | binary | **4 label spellings of 2 outcomes** (trailing dot); `?` placeholders; categoricals; 48,842 rows | 0002, 0010, 0023; **label spellings need engine item E5** |
| 4 | Dry Bean | multiclass | 7 labels; correlated shape features | 0002, 0017 |
| 5 | Covertype | multiclass | 581,012 rows; imbalance; one-hot indicator blocks | 0010 (0/1 stay numeric), 0015, 0017 |
| 6 | Anuran Calls | multilabel | 3 nested categorical targets; repeated recordings | 0002, 0004, 0016, 0018 |
| 7 | Abalone | regression | categorical feature; count outcome; mixed EDA summary | 0012, 0019 |
| 8 | Bike Sharing | regression | two columns sum to the target; hourly time order; date string | 0003, 0004, 0008, 0010, 0016, 0019 |
| 9 | Energy Efficiency | multi-output regression | two targets; coded feature names | 0002, 0019 |
| 10 | Seeds | clustering | evaluation label removed; small n | 0021 |
| 11 | Online Retail | clustering | transactions; reversals; codes; 541,909 rows; date string | 0010, 0015, 0020, 0021, 0024 |
| 12 | Optical Digits | representation | evaluation label removed; 64 homogeneous features | 0002, 0022 |

## Not rails: engine and template items for the execution agent

These are code changes, outside the rails. Apply them at a round boundary, each with a ledger entry and regression test:

- **E1 Metric names.** Normalise case and common aliases (`RMSE` → `rmse`, `auc` → `roc_auc`, `f1_macro` → `macro_f1`) in a before-validator on `StudyProposal.primary_metric` (`src/mlca/autonomous/inference.py`).
- **E2 One metric table.** The default metric per problem type is copied in `autonomous/inference.py`, `autonomous/runner.py`, `engine/checks.py` and `engine/data_review.py`. Keep one source.
- **E3 Wall-clock limit per model call.** `timeout_s` is an I/O timeout (a call took 459 s at `timeout_s=90`). Add a hard deadline that routes to the existing provider cooldown in `runner.drive`.
- **E4 Unsupervised templates.** `clustering` and `representation` still ask "Which column do you want to predict?" and keep `count_target` and `freeze_stratified`. Reword, or remove them for these templates. `RL-0021` and `RL-0022` only mitigate this. Also replace the shared generic `methods_text` (needed for Part C).
- **E5 Outcome label spellings.** Setup sees only unique counts, so an outcome with two labels written four ways (trailing punctuation, whitespace, case) cannot be declared binary: the engine requires exactly two observed values. Option: show the Navigator the distinct values of low-cardinality outcome candidates (category names only, never rows), and allow a recorded label mapping that is validated before the cardinality check. **Approved by the author on 16 October 2026:** the setup inventory shows distinct values (at most 20 per column) and numeric summaries for every column, recorded in the egress ledger. A `label_map` with a reason may merge spellings of one label.
- **E6 Feature record.** `fit_record` logs the fitted column names (names only); evidence for the external leakage outcome.
- **E7 Group values for internal folds.** Check that the group column stays available in the training partition (outside the feature list) so RL-0016 can pass `groups=`; if not, expose it.
- **Engine checks (optional, kind `check`, need registered functions in `src/mlca/rails/checks.py`):**
  - `leakage_screen`, after `split`: the RL-0008 screen enforced by the engine, warning only, value-free detail.
  - `perfect_score_sentinel`, after `validate`: primary validation metric ≥ 0.995 (AUC/R²) or error ≈ 0 fires a rail and asks for a stated reason before test. This bears on R2-4/5.

## Activation (execution agent, after round 2 has finished)

1. Do not activate while any batch is running.
2. Copy `RL-0002.yaml` … `RL-0024.yaml` into `rails/`, set `rails/VERSION` to `rails-0.3`, and keep `RL-0001.yaml`.
3. Add ledger entry **L-0002** in `rails/LEDGER.md`: "Design pass for all 12 development tasks, 16 October 2026. Rails RL-0002 to RL-0024. Basis: rounds 1–2 (O) and task types (A), per the table in `rails/proposed/rails-0.3/DESIGN.md`. Proposed by Claude Code; author review at Part C."
4. Run the genericity test and the suite. Commit locally as one change, separately from any engine items (E1–E5) and from the model switch (STUDY_DESIGN §3: model and rails are not changed in the same batch).
5. If live runs show that a rail hurts or never applies, remove or revise it with its own ledger entry. Do not delete history.

## Revised after the execution agent's review (16 October 2026)

RL-0007 (near-uniqueness too broad), RL-0008 (correlation is a warning, not proof), RL-0009 (dense output and memory), RL-0014 (the Worker sees sanitised diagnostics, not full tracebacks), RL-0016 (`fit_record` rejects fold subsets; group values must be available) and RL-0020 (aggregate before the split, in `build_entities`) were revised as above; the log1p part of RL-0020 became RL-0024. E5 became an author decision; E6 and E7 added.

## Open points for the author's review

- RL-0005 limits exploration to one alternative model. This favours completion over performance, in line with the study question.
- RL-0015 thresholds (100,000 rows; 10,000-row subsamples) and RL-0017 (10%) are fixed values. They become study parameters at the freeze.
