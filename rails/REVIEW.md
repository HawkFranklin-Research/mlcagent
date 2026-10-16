# Rails review — work order 05 baseline, live batch pending

This is a review draft, not acceptance or a freeze. All 24 active rails are
instructions; engine enforcement is listed separately. No held-out data was
inspected. Rounds 1–2 are exploratory evidence, not a comparison against the
DeepSeek baseline, which also changes the engine.

RL-0001 remains provisional: its output-budget evidence is one setup failure.
The remaining rails are a consolidated design pass, mixing observed failures
and anticipated task-type issues as individually documented in DESIGN.md.
The post-acceptance ablation is still pending.

## RL-0001

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0001.yaml; ledger: L-0001 in LEDGER.md.
- Exact instruction:

> During study-setup inference, give one concise proposal and a one-sentence justification. Include an alternative only for a concrete unresolved scientific ambiguity; otherwise return an empty alternatives list. Do not invent an unrelated prediction objective to populate the list.

- Rationale: Avoid unnecessary alternative proposals and excessive setup output before analysis can begin.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0002

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0002.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Choose problem_type from the schema. Two observed values in the outcome: binary. Three or more discrete labels: multiclass. Several categorical outcome columns describing the same row at different levels of detail: multilabel, with all of them as targets. One numeric measurement or count: regression. Two or more numeric outcomes recorded together: multioutput_regression. If no column is a plausible outcome, choose clustering when rows are entities or events to segment, and representation when the table is many homogeneous numeric features of one kind. Prefer the task the table was evidently assembled for over an incidental column.

- Rationale: Setup proposals chose a binary outcome as multiclass and a multi-output outcome set as a single target; the problem type decides every later step.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0003

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0003.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> List as leakage_suspects every column that is a component, sum, difference, rescaling or recoding of a target, or that is known only after the outcome (for example the raw score a binary target was derived from, or partial counts that add up to a total). List as identifier_suspects row keys, record numbers and codes with nearly one unique value per row. Never propose either kind as a feature.

- Rationale: A target reconstructed from its parts gives near-perfect scores without learning anything; setup is the only point where the agent names such columns before the split.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0004

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0004.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Set group_column when a non-target column repeats across rows and identifies the source unit (subject, recording, customer, device), so its rows must stay in one partition. List time_columns when rows carry timestamps or calendar parts and the aim is to predict later periods. Leave both empty when no such column exists; do not invent them.

- Rationale: Rows from one source unit or one period on both sides of the split inflate validation and test scores; the split can respect them only if setup declares them.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0005

- Kind: instruction; roles: navigator; events: model, validate; problem types: all.
- Executable source: RL-0005.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Reach one complete, scored baseline before exploring. Try at most one alternative kind of model before freezing a candidate for test, and stop tuning once both have a recorded validation metric. Finishing the workflow comes before further optimisation.

- Rationale: Each extra model turn costs requests, time and new failure chances; the study measures completion of a valid workflow, not leaderboard performance.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0006

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0006.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Read outcomes and exclusions only from the _protocol JSON: targets in _protocol['targets'], dropped columns in _protocol['excluded_columns'], the group in _protocol['group_column'], task details in _protocol['task']. The Brief in this order is a different object; never index _protocol with Brief keys. If a needed key is missing, raise an error that lists the available top-level keys instead of guessing a nested path.

- Rationale: A model-step script failed with a KeyError after reading the protocol through keys that exist only in the Brief.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0007

- Kind: instruction; roles: worker; events: data, eda, split, preprocess, features, model, validate, test, interpret; problem types: all.
- Executable source: RL-0007.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Define the feature columns once: every column of the frozen table except the targets, the excluded columns and the group column, and except key-like columns: text codes or integer sequences whose values are all distinct and carry no measurement. Continuous measurements are never identifiers, however many distinct values they have. Use exactly that list in every step, and never let a target or excluded column reach a fitted transformer or model.

- Rationale: Feature lists rebuilt differently in each step let outcome-derived or key columns into models and break saved pipelines between steps.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0008

- Kind: instruction; roles: worker; events: preprocess; problem types: all.
- Executable source: RL-0008.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Before fitting preprocessing, screen the candidate features on training rows without fitting a model. Exclude, in the saved preprocessing, only features that are confirmed derivations of a target: exact equality with it, or a row sum of up to three non-negative columns that equals it on every training row. Features with absolute correlation of 0.98 or more with a target are a warning, not proof: keep them and print one line with their names. Print one line naming any excluded feature and the reason.

- Rationale: Setup sees only the schema, so leakage visible only in values must be caught on training rows; high correlation alone can be a legitimate strong predictor, so only exact derivations are removed.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0009

- Kind: instruction; roles: worker; events: preprocess, features, model; problem types: all.
- Executable source: RL-0009.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Keep feature names through preprocessing. When the encoded output has at most 300 columns, call set_output(transform='pandas') on ColumnTransformer and Pipeline objects and use OneHotEncoder(handle_unknown='ignore', sparse_output=False). When it would be wider, keep sparse output inside one Pipeline that starts from the raw feature DataFrame, take names from get_feature_names_out(), and never pass that output to a transformer that selects columns by name.

- Rationale: Transformers that output NumPy arrays lose column names and the next name-based transformer fails; dense output of very wide encodings exhausts memory on large tables.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0010

- Kind: instruction; roles: worker; events: preprocess; problem types: all.
- Executable source: RL-0010.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Before encoding, sort feature columns into types: numeric; low-cardinality categorical (one-hot); text or code columns with more unique values than 5% of rows (drop, or use a frequency encoding fitted on training rows, never one-hot); date or time strings (parse with pandas.to_datetime, derive numeric parts such as hour, day of week and month, then drop the raw string). Integer 0/1 indicator columns stay numeric.

- Rationale: One-hot encoding codes or raw timestamps creates thousands of columns, exhausts memory on large tables and memorises rows.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0011

- Kind: instruction; roles: worker; events: features, model, validate, test, interpret; problem types: all.
- Executable source: RL-0011.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Saved transformers from earlier steps may already contain the earlier preprocessing. Before combining them, check isinstance(obj, Pipeline) and obj.named_steps to see whether the later object includes the earlier one; build on the most complete saved pipeline that accepts the raw feature DataFrame and append only the new estimator. Never place a saved pipeline after a step it already contains, and never pass NumPy arrays to a transformer that selects columns by name.

- Rationale: Model steps chained a saved preprocessor before a saved selector that already contained it, applying preprocessing twice and failing on arrays.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0012

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0012.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Summary tables have one type per column: use NaN, not empty strings, for values that do not apply, or put numeric and categorical summaries in separate columns. Keep at most 50 rows and 12 columns; for wide summaries, place variables in rows and statistics in columns.

- Rationale: An EDA summary mixed empty strings into a numeric column and could not be saved.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0013

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0013.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Keep each script short and direct, about 120 lines or fewer: loop over columns instead of repeating blocks, no commented-out alternatives, no long docstrings, no restating of these instructions. A complete short script is better than an elaborate one that is cut off.

- Rationale: Worker responses exhausted the output allowance before the script was complete.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0014

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0014.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> When repairing, read the error type and message in the diagnostics first and change the smallest part of the script that causes it; keep the approach, inputs and outputs. A message about specifying columns with strings on non-dataframes means an array reached a name-based transformer (see RL-0009 and RL-0011). A KeyError on a JSON key means a guessed structure; use the keys the file has. Messages starting with 'MLCA:' state an engine rule; comply, do not work around it.

- Rationale: Repairs rewrote whole scripts and reintroduced the same fault in all three attempts.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0015

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0015.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> When the training table has more than 100000 rows, avoid methods whose cost grows with the square of the row count (full silhouette, kernel SVMs, pairwise distances, t-SNE, agglomerative clustering) and prefer linear models with saga or SGD solvers, HistGradientBoosting or MiniBatchKMeans. Every fit_record call still uses all training rows; compute expensive diagnostics that fit nothing on a fixed-seed subsample of at most 10000 rows and print its size.

- Rationale: Tables with hundreds of thousands of rows exceed sandbox time and memory with quadratic methods, and fit_record accepts only the full frozen training index.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0016

- Kind: instruction; roles: worker; events: model, validate; problem types: all.
- Executable source: RL-0016.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Tune only inside one fit_record call on the full training rows, with a search object (GridSearchCV or RandomizedSearchCV) whose folds respect the design; never call fit_record on fold subsets. If _protocol['group_column'] is set, use cv=GroupKFold and pass the training rows' group values through fit_record as groups=. If the task lists time columns, use cv=TimeSeriesSplit only when the frozen training rows are already in time order (never reorder them); otherwise skip internal folds and select on the validation partition. Do not use the group key as a feature.

- Rationale: Internal folds that ignore groups or time repeat the leakage the frozen split avoids, and fit_record accepts only the full frozen training index in its stored order.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0017

- Kind: instruction; roles: worker; events: model, validate, test; problem types: binary, multiclass.
- Executable source: RL-0017.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> For roc_auc take the probability column of the positive label: predict_proba(X)[:, list(model.classes_).index(positive)], with the positive label from _protocol or else model.classes_[1]. For roc_auc_ovr pass the full probability matrix with labels=model.classes_, multi_class='ovr', average='macro'. Keep outcome labels as stored. When the smallest outcome category is under 10% of training rows, set class_weight='balanced' where supported.

- Rationale: Probability columns misaligned with labels silently invert or break ROC AUC; rare categories are otherwise ignored by default losses.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0018

- Kind: instruction; roles: worker; events: model, validate, test, interpret; problem types: multilabel.
- Executable source: RL-0018.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> The targets are several categorical columns predicted together. Wrap single-output estimators in MultiOutputClassifier, or use one that supports several outputs, and fit on the target DataFrame in _protocol['targets'] order. predict_proba then returns one array per target. For macro_f1 compute f1_score(average='macro') per target from predict, and report the unweighted mean over targets as the headline value, with per-target values in the saved table.

- Rationale: Multi-output predictions have a different shape from single-output ones; metric code written for one target fails or scores only the first.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0019

- Kind: instruction; roles: worker; events: model, validate, test, interpret; problem types: regression, multioutput_regression.
- Executable source: RL-0019.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Report every metric on the original scale of the targets. For non-negative counts or strongly right-skewed outcomes, prefer a Poisson loss or TransformedTargetRegressor with log1p and expm1, and invert before scoring. With several numeric targets, fit them together in _protocol['targets'] order (natively or with MultiOutputRegressor), and report the metric per target and their unweighted mean as the headline value.

- Rationale: Scores on a transformed scale are not comparable, and multi-output regression must keep target order between fitting and scoring.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0020

- Kind: instruction; roles: worker; events: eda; problem types: clustering.
- Executable source: RL-0020.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> If rows are transactions rather than entities, build one row per entity in the entity-building step, before the split, never after partitioning: drop rows without an entity key, handle reversing rows (negative amounts, returns) by an explicit rule printed in one line, and aggregate deterministically (recency against the last date in the table, frequency, total and mean value), with no fitted transform.

- Rationale: Clustering raw transactions segments receipts, not entities; aggregating after the split would change row identities and conflict with the frozen training index.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0021

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; problem types: clustering.
- Executable source: RL-0021.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> There is no outcome in this project: never treat any column as a label or count its categories as one. Choose the cluster count only from internal criteria (silhouette, Davies-Bouldin, Calinski-Harabasz, stability). Scale features before distance-based methods. Compute silhouette with sample_size at most 10000 and a fixed random_state. Required per-row outputs hold the assigned cluster for each row_id.

- Rationale: Template steps written for classification ask for an outcome; unsupervised projects must not invent one, and full silhouette is quadratic in rows.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0022

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; problem types: representation.
- Executable source: RL-0022.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> There is no outcome in this project: never treat any column as a label. Scale inputs to a common range fitted on training rows, and report reconstruction error in that scaled space, saying so. An autoencoder may be an MLPRegressor trained to reproduce its scaled input; its embedding is the middle hidden layer computed from coefs_ and intercepts_ without refitting. Record the embedding dimension. Required per-row outputs hold the embedding for each row_id.

- Rationale: Representation steps need a fitted encoder whose embeddings can be extracted without refitting, so that an external scorer can evaluate them.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0023

- Kind: instruction; roles: worker; events: data, eda, preprocess; problem types: all.
- Executable source: RL-0023.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Check text columns for placeholder tokens that stand for missing values (a lone '?', '-', 'NA', 'N/A', or whitespace-only strings) and for surrounding whitespace. Strip whitespace and convert only such placeholders to missing inside the fitted preprocessing, and print one line naming the placeholders found and how many columns contain them.

- Rationale: Published tables mark missing values with placeholder strings; left as text they become spurious categories and hide the true amount of missing data.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## RL-0024

- Kind: instruction; roles: worker; events: preprocess; problem types: clustering, representation.
- Executable source: RL-0024.yaml; ledger: L-0002 in LEDGER.md.
- Exact instruction:

> Apply log1p to heavy-tailed non-negative features (such as monetary totals and counts) inside the fitted preprocessing, before scaling.

- Rationale: Heavy tails let a few extreme rows dominate distance- and reconstruction-based methods.
- Cause/basis: individual row in proposed/rails-0.3/DESIGN.md (O = observed rounds 1–2, A = anticipated from development task types).
- Before/after: earlier exploratory evidence retained; new batch-01 pending. No measured improvement claimed.
- Genericity: the instruction concerns data types, model interfaces or workflow boundaries; it contains no development dataset/column identifier or model ID.

## Offline gate

Native full gate: 408 passed, 1 skipped; experiments: 18 passed; Ruff passes.
The initial deadline-adapter compatibility regression was fixed and retained
as B-0010. Live batch-01 remains pending at this baseline commit.

## Engine changes (not rails)

- B-0001: setup response contract and failed-setup accounting (c5ea681).
- B-0002–B-0005 / E1–E4: aliases, metric registry, hard call deadline and unsupervised template wording (d48b0f8).
- B-0006 / E5: authorized setup value information and validated label spelling maps (9026276).
- B-0007–B-0008 / E6–E7: fitted columns and training groups (bf8814b).
- B-0009: shared pacing, explicit unlimited budgets and rails-off snapshot (c448e56).
- Researcher leakage metadata and external checks do not enter agent prompts.

## Rejected approaches

- Expected manifest tasks/targets in the prompt: oracle leakage.
- Dataset-specific instructions or silently replacing the Worker with reference code: outside the scientific design.
- Correlation alone automatically removes a predictor: insufficient evidence of leakage.
- Treating almost-unique continuous measurements as identifiers: scientifically unsound.
- Dense one-hot output for every categorical table: potential memory blow-up.
- Fitting individual CV folds with fit_record: conflicts with the unchanged full-training-index rule; use one search estimator instead.
- Claiming unavailable fitted columns, costs or split evidence are clean/zero: unsupported.

## Historical review (superseded by the status above)

The following text preserves the earlier interim review verbatim.

# Rails review — development in progress

## RL-0001

- Kind: instruction; scope: Navigator, onboard, all problem types; commit `900bd07`.
- Text: see RL-0001.yaml (the executable source of this instruction).
- Cause: L-0001; Round 1 setup output truncation, before any Worker execution.
- Before: rails-0.0, 0/12 workflow completions; one truncated setup output.
- After: rails-0.2 fresh round pending. Offline injection/genericity checks pass.
- Generic because it concerns proposal brevity and concrete ambiguity, with no
  dataset-specific target or method. It is not a promise that hidden reasoning
  or provider output caps can be controlled.

## Engine fixes (not rails)

B-0001 (`c5ea681`) repairs an inconsistent advertised setup contract and preserves failed
setup accounting. Details and evidence are in LEDGER.md. Existing semantic
checks now participate in bounded structured repair; no check is removed.

## Rejected approaches

- Supplying manifest targets or expected tasks to inference: rejected as oracle
  leakage. The manifest remains external evaluation metadata.
- Mapping every invalid metric to the expected metric silently: rejected;
  advertise allowed IDs and require a corrected model proposal instead.
- Hard-coding a particular table's target or switching to reference analysis:
  rejected. All analysis code must still come from the Worker.

This is an interim review, not a freeze or successful acceptance report.
