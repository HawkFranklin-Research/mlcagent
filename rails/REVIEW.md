# Rails review — rails-0.11 after batch-09

All 27 rails are instructions; no new scientific checks/defaults. Development
only, no acceptance, ablation or freeze. Held-out files untouched.
Batch 03: four new qualifying completions, seven tables qualified across the
series. Evidence: experiments bench/dev-loop/batch-03/{REPORT,REVIEW}.md and
curated/MANIFEST.csv. Aggregate changes do not isolate individual rail effects.
RL-0001 remains provisional; output truncation is measured separately.

L-0005 revises three existing rails: RL-0004 requires time for consecutive
periods regardless of prediction aim (Bike); RL-0018 evaluates categorical
outputs separately (Anuran); RL-0022 distinguishes PCA reconstruction from
MLP prediction (Optical Digits). Other rails retain prior evidence and design
basis. Engine fixes and the prospective Retail criterion are separate.

Rejected shortcuts: no dataset-specific columns/targets, relaxed fit/test rules,
reference-code substitution, hidden-label access or historical rescoring.

## Batch04–05 evidence update

Anuran, Seeds and Bike newly qualify, bringing the series to10/12 once;
acceptance and ablation remain pending. Batch04/05 source identities match;
only requested effort changes to low in05. Per-table completion and limitations:
experiments4a380e1 and9447df6, each REPORT/REVIEW and curated hashes.
Retail04 completes with clean applicable leakage checks but extra date field;
Retail05 recommends preparation but invalid auxiliary metadata triggers a bad
fallback. Digits05 corrects reconstruction then emits an undeclared row file.
RL0022 is refined inL0006; no isolated rail-effect claim. Seeds external ARI/NMI
are evaluator measurements, never agent work or a basis for tuning rails.

## Batch06 follow-up

No new qualifying study; Digits passes validation then fails with None returned
by a private activation helper; Retail prepares entities but renames/drops its
declared constraint columns. Evidence experiments ef3d703. L0007 refines existing
analysis-unit, metadata-preservation and embedding instructions. B0024–26 are
separate engine/output/storage corrections. Source cache v3 preserves matching
policy; legacy projects remain readable/writable without silent migration.
No hidden-label tuning or reference analysis;10/12 qualified once, not acceptance.

## Batch07 follow-up

Optical Digits qualifies end-to-end (11/12 tables qualified). Online Retail completes
all 12 steps to report and passes all three leakage checks, but fails setup agreement
due to time_columns: ["InvoiceDate"]. Evidence experiments 9be8c34. L-0008 refines
RL-0004 to clarify that for static entity clustering from transactional records,
time_columns should be left empty.

## First acceptance batch follow-up

24/36 qualified on direct `deepseek-flash`. Engine fixes B-0027–B-0031 (nested
empty alternatives, display-text clipping, timestamp-safe time split, protected
fit inputs, setup messages). L-0009 refines RL-0002, RL-0003, RL-0010 and RL-0018;
their exact current text is in the YAML files (the quotes below predate L-0009
for those four rails).

## RL-0001

- Kind: instruction; roles: navigator; events: onboard; tasks: all.
- Source: RL-0001.yaml; ledger: L-0001; introduced: rails-0.2.
- Exact instruction:

> During study-setup inference, give one concise proposal and a one-sentence justification. Include an alternative only for a concrete unresolved scientific ambiguity; otherwise return an empty alternatives list. Do not invent an unrelated prediction objective to populate the list.

- Rationale: Avoid unnecessary alternative proposals and excessive setup output before analysis can begin.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0002

- Kind: instruction; roles: navigator; events: onboard; tasks: all.
- Source: RL-0002.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Choose problem_type from the schema. Two observed values in the outcome: binary. Three or more discrete labels: multiclass. Several categorical outcome columns describing the same row at different levels of detail: multilabel, with all of them as targets. One numeric measurement or count: regression. Two or more numeric outcomes recorded together: multioutput_regression. If no column is a plausible outcome, choose clustering when rows are entities or events to segment, and representation when the table is many homogeneous numeric features of one kind. Prefer the task the table was evidently assembled for over an incidental column.

- Rationale: Setup proposals chose a binary outcome as multiclass and a multi-output outcome set as a single target; the problem type decides every later step.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0003

- Kind: instruction; roles: navigator; events: onboard; tasks: all.
- Source: RL-0003.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> List as leakage_suspects every column that is a component, sum, difference, rescaling or recoding of a target, or that is known only after the outcome (for example the raw score a binary target was derived from, or partial counts that add up to a total). List as identifier_suspects row keys, record numbers and codes with nearly one unique value per row. Never propose either kind as a feature.

- Rationale: A target reconstructed from its parts gives near-perfect scores without learning anything; setup is the only point where the agent names such columns before the split.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0004

- Kind: instruction; roles: navigator; events: onboard; tasks: all.
- Source: RL-0004.yaml; ledger: L-0008; introduced: rails-0.3.
- Exact instruction:

> Set group_column when a non-target column repeats across rows and identifies the source unit (subject, recording, customer, device), so its rows must stay in one partition. List time_columns when rows are consecutive periods of one series, regardless of the stated prediction aim, or when the aim is to predict later periods. Use columns that establish chronological order, not redundant seasonal encodings. Leave both empty when no such column exists; do not invent them. Declare constraints for the final analysis units, not merely every raw event field. When clustering or segmenting static entities from transactional records, leave time_columns empty; transaction timestamps used only to aggregate static features (such as recency relative to an observation date) are not time columns for partitioning. Consecutive periods of a single series still require chronology.

- Rationale: Rows from one source unit or one period on both sides of the split inflate validation and test scores; the split can respect them only if setup declares them.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0005

- Kind: instruction; roles: navigator; events: model, validate; tasks: all.
- Source: RL-0005.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Reach one complete, scored baseline before exploring. Try at most one alternative kind of model before freezing a candidate for test, and stop tuning once both have a recorded validation metric. Finishing the workflow comes before further optimisation.

- Rationale: Each extra model turn costs requests, time and new failure chances; the study measures completion of a valid workflow, not leaderboard performance.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0006

- Kind: instruction; roles: worker; events: all; tasks: all.
- Source: RL-0006.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Read outcomes and exclusions only from the _protocol JSON: targets in _protocol['targets'], dropped columns in _protocol['excluded_columns'], the group in _protocol['group_column'], task details in _protocol['task']. The Brief in this order is a different object; never index _protocol with Brief keys. If a needed key is missing, raise an error that lists the available top-level keys instead of guessing a nested path.

- Rationale: A model-step script failed with a KeyError after reading the protocol through keys that exist only in the Brief.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0007

- Kind: instruction; roles: worker; events: data, eda, split, preprocess, features, model, validate, test, interpret; tasks: all.
- Source: RL-0007.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Define the feature columns once: every column of the frozen table except the targets, the excluded columns and the group column, and except key-like columns: text codes or integer sequences whose values are all distinct and carry no measurement. Continuous measurements are never identifiers, however many distinct values they have. Use exactly that list in every step, and never let a target or excluded column reach a fitted transformer or model.

- Rationale: Feature lists rebuilt differently in each step let outcome-derived or key columns into models and break saved pipelines between steps.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0008

- Kind: instruction; roles: worker; events: preprocess; tasks: all.
- Source: RL-0008.yaml; ledger: L-0003; introduced: rails-0.3.
- Exact instruction:

> Before fitting preprocessing, screen the candidate features on training rows without fitting a model. Exclude, in the saved preprocessing, only features that are confirmed derivations of a target: exact equality with it, or a row sum of up to three non-negative columns that equals it on every training row. Features with absolute correlation of 0.98 or more with a target are a warning, not proof: keep them and print one line with their names. Print one line naming any excluded feature and the reason. Correlation warnings apply only to numeric outcomes; never coerce categorical labels to floats for Pearson correlation. Skip that numeric screen for categorical outcomes and retain exact-derivation checks.

- Rationale: Setup sees only the schema, so leakage visible only in values must be caught on training rows; high correlation alone can be a legitimate strong predictor, so only exact derivations are removed.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0009

- Kind: instruction; roles: worker; events: preprocess, features, model; tasks: all.
- Source: RL-0009.yaml; ledger: L-0003; introduced: rails-0.3.
- Exact instruction:

> Keep feature names through preprocessing. When the encoded output has at most 300 columns, call set_output(transform='pandas') on ColumnTransformer and Pipeline objects and use OneHotEncoder(handle_unknown='ignore', sparse_output=False). When it would be wider, keep sparse output inside one Pipeline that starts from the raw feature DataFrame, take names from get_feature_names_out(), and never pass that output to a transformer that selects columns by name. Use set_output only with components that support it; prefer built-in sklearn transformers with get_feature_names_out rather than custom components.

- Rationale: Transformers that output NumPy arrays lose column names and the next name-based transformer fails; dense output of very wide encodings exhausts memory on large tables.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0010

- Kind: instruction; roles: worker; events: preprocess; tasks: all.
- Source: RL-0010.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Before encoding, sort feature columns into types: numeric; low-cardinality categorical (one-hot); text or code columns with more unique values than 5% of rows (drop, or use a frequency encoding fitted on training rows, never one-hot); date or time strings (parse with pandas.to_datetime, derive numeric parts such as hour, day of week and month, then drop the raw string). Integer 0/1 indicator columns stay numeric.

- Rationale: One-hot encoding codes or raw timestamps creates thousands of columns, exhausts memory on large tables and memorises rows.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0011

- Kind: instruction; roles: worker; events: features, model, validate, test, interpret; tasks: all.
- Source: RL-0011.yaml; ledger: L-0003; introduced: rails-0.3.
- Exact instruction:

> Saved transformers from earlier steps may already contain the earlier preprocessing. Before combining them, check isinstance(obj, Pipeline) and obj.named_steps to see whether the later object includes the earlier one; build on the most complete saved pipeline that accepts the raw feature DataFrame and append only the new estimator. Never place a saved pipeline after a step it already contains, and never pass NumPy arrays to a transformer that selects columns by name. Inspect feature_names_in_ for each loaded object and preserve its exact input columns and order. A saved selector may already wrap preprocessing: use that selector as the only frontend, or chain preprocessing once before a bare selector. Never feed derived or renamed columns back into a raw-column frontend.

- Rationale: Model steps chained a saved preprocessor before a saved selector that already contained it, applying preprocessing twice and failing on arrays.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0012

- Kind: instruction; roles: worker; events: all; tasks: all.
- Source: RL-0012.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Summary tables have one type per column: use NaN, not empty strings, for values that do not apply, or put numeric and categorical summaries in separate columns. Keep at most 50 rows and 12 columns; for wide summaries, place variables in rows and statistics in columns.

- Rationale: An EDA summary mixed empty strings into a numeric column and could not be saved.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0013

- Kind: instruction; roles: worker; events: all; tasks: all.
- Source: RL-0013.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Keep each script short and direct, about 120 lines or fewer: loop over columns instead of repeating blocks, no commented-out alternatives, no long docstrings, no restating of these instructions. A complete short script is better than an elaborate one that is cut off.

- Rationale: Worker responses exhausted the output allowance before the script was complete.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0014

- Kind: instruction; roles: worker; events: all; tasks: all.
- Source: RL-0014.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> When repairing, read the error type and message in the diagnostics first and change the smallest part of the script that causes it; keep the approach, inputs and outputs. A message about specifying columns with strings on non-dataframes means an array reached a name-based transformer (see RL-0009 and RL-0011). A KeyError on a JSON key means a guessed structure; use the keys the file has. Messages starting with 'MLCA:' state an engine rule; comply, do not work around it.

- Rationale: Repairs rewrote whole scripts and reintroduced the same fault in all three attempts.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0015

- Kind: instruction; roles: worker; events: all; tasks: all.
- Source: RL-0015.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> When the training table has more than 100000 rows, avoid methods whose cost grows with the square of the row count (full silhouette, kernel SVMs, pairwise distances, t-SNE, agglomerative clustering) and prefer linear models with saga or SGD solvers, HistGradientBoosting or MiniBatchKMeans. Every fit_record call still uses all training rows; compute expensive diagnostics that fit nothing on a fixed-seed subsample of at most 10000 rows and print its size.

- Rationale: Tables with hundreds of thousands of rows exceed sandbox time and memory with quadratic methods, and fit_record accepts only the full frozen training index.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0016

- Kind: instruction; roles: worker; events: model, validate; tasks: all.
- Source: RL-0016.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Tune only inside one fit_record call on the full training rows, with a search object (GridSearchCV or RandomizedSearchCV) whose folds respect the design; never call fit_record on fold subsets. If _protocol['group_column'] is set, use cv=GroupKFold and pass the training rows' group values through fit_record as groups=. If the task lists time columns, use cv=TimeSeriesSplit only when the frozen training rows are already in time order (never reorder them); otherwise skip internal folds and select on the validation partition. Do not use the group key as a feature.

- Rationale: Internal folds that ignore groups or time repeat the leakage the frozen split avoids, and fit_record accepts only the full frozen training index in its stored order.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0017

- Kind: instruction; roles: worker; events: model, validate, test; tasks: binary, multiclass.
- Source: RL-0017.yaml; ledger: L-0004; introduced: rails-0.3.
- Exact instruction:

> For binary roc_auc, align the positive probability column with model.classes_ using the declared positive label, or model.classes_[1] when none is declared. Pass a binary indicator for that same label as y_true; roc_auc_score does not accept pos_label. Preserve the original labels for other metrics and record the positive-label convention. For roc_auc_ovr pass the full aligned probability matrix with labels=model.classes_, multi_class='ovr', average='macro'. When the smallest outcome category is under 10% of training rows, set class_weight='balanced' where supported.

- Rationale: Probability columns misaligned with labels silently invert or break ROC AUC; rare categories are otherwise ignored by default losses.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0018

- Kind: instruction; roles: worker; events: model, validate, test, interpret; tasks: multilabel.
- Source: RL-0018.yaml; ledger: L-0005; introduced: rails-0.3.
- Exact instruction:

> Several categorical targets need MultiOutputClassifier or an estimator supporting multiple outputs, with the target DataFrame in _protocol['targets'] order. predict_proba returns one array per target. Do not pass the whole multiclass-multioutput categorical matrix to f1_score, accuracy_score or hamming_loss; these do not support this target form. Compute each score on each target separately and average the per-target values; compute subset accuracy directly as the mean of rows whose target predictions all match. Compute f1_score(average='macro') separately on each target's one-dimensional true and predicted labels, then report the unweighted mean and per-target values. Both vectors must have the same native label type; an object array of encoded integers can be rejected as unknown. Preserve categorical labels directly, or save the training-fitted target encoders with the model and reuse their unchanged mappings. Never fit an encoder during validation or test.

- Rationale: Multi-output predictions have a different shape from single-output ones; metric code written for one target fails or scores only the first.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0019

- Kind: instruction; roles: worker; events: model, validate, test, interpret; tasks: regression, multioutput_regression.
- Source: RL-0019.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Report every metric on the original scale of the targets. For non-negative counts or strongly right-skewed outcomes, prefer a Poisson loss or TransformedTargetRegressor with log1p and expm1, and invert before scoring. With several numeric targets, fit them together in _protocol['targets'] order (natively or with MultiOutputRegressor), and report the metric per target and their unweighted mean as the headline value.

- Rationale: Scores on a transformed scale are not comparable, and multi-output regression must keep target order between fitting and scoring.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0020

- Kind: instruction; roles: navigator, worker; events: eda; tasks: clustering.
- Source: RL-0020.yaml; ledger: L-0007; introduced: rails-0.3.
- Exact instruction:

> If the proposed clustering units are entities but the input rows are repeated transactions, the Navigator must recommend build_entities before a distribution-only EDA action completes the event. In that entity-building step, before the split, the Worker builds one row per entity: drop rows without an entity key, handle reversing rows (negative amounts, returns) by an explicit rule printed in one line, and aggregate deterministically (recency against the last date in the table, frequency, total and mean value), with no fitted transform. Save the declared prepared-data artifact so the engine freezes the entity rows. Do not aggregate after partitioning or pretend transaction-level clustering satisfies an entity-level aim. Preserve the declared group column as a complete explicit column with the same name, never a generic renamed identifier or index alone. Preserve declared chronological ordering columns with a documented, consistent entity-level time aggregation; do not silently discard them.

- Rationale: A distribution-only EDA completed before entity preparation, leaving missing group keys and the wrong analysis rows at the split.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0021

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; tasks: clustering.
- Source: RL-0021.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> There is no outcome in this project: never treat any column as a label or count its categories as one. Choose the cluster count only from internal criteria (silhouette, Davies-Bouldin, Calinski-Harabasz, stability). Scale features before distance-based methods. Compute silhouette with sample_size at most 10000 and a fixed random_state. Required per-row outputs hold the assigned cluster for each row_id.

- Rationale: Template steps written for classification ask for an outcome; unsupervised projects must not invent one, and full silhouette is quadratic in rows.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0022

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; tasks: representation.
- Source: RL-0022.yaml; ledger: L-0007; introduced: rails-0.3.
- Exact instruction:

> There is no outcome in this project: never treat any column as a label. Fit scaling on training rows only. Inspect each saved pipeline's final estimator and reuse its frontend once; compare reconstruction error in that frontend's feature space, saying so. PCA has no predict method: reconstruct with inverse_transform(transform(X)) on its final PCA component, not an inverse of the whole preprocessing pipeline. An MLPRegressor reconstructs with predict, never inverse_transform. Its embedding is the middle hidden layer computed from coefs_ and intercepts_ without refitting; PCA coordinates come from transform. Record embedding dimension. Only emit embeddings when the action declares a per-row output, with row_id and partition as explicit columns. Metric-only validation must not create embedding files. Avoid private sklearn ACTIVATIONS: they mutate in place and return None. Use public NumPy/SciPy activation results and propagate through each hidden layer up to the actual middle bottleneck, explicitly returning a finite 2D array of identical width for train and test.

- Rationale: Representation steps need a fitted encoder whose embeddings can be extracted without refitting, so that an external scorer can evaluate them.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0023

- Kind: instruction; roles: worker; events: data, eda, preprocess; tasks: all.
- Source: RL-0023.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Check text columns for placeholder tokens that stand for missing values (a lone '?', '-', 'NA', 'N/A', or whitespace-only strings) and for surrounding whitespace. Strip whitespace and convert only such placeholders to missing inside the fitted preprocessing, and print one line naming the placeholders found and how many columns contain them.

- Rationale: Published tables mark missing values with placeholder strings; left as text they become spurious categories and hide the true amount of missing data.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0024

- Kind: instruction; roles: worker; events: preprocess; tasks: clustering, representation.
- Source: RL-0024.yaml; ledger: L-0002; introduced: rails-0.3.
- Exact instruction:

> Apply log1p to heavy-tailed non-negative features (such as monetary totals and counts) inside the fitted preprocessing, before scaling.

- Rationale: Heavy tails let a few extreme rows dominate distance- and reconstruction-based methods.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0025

- Kind: instruction; roles: worker; events: preprocess, features, model; tasks: all.
- Source: RL-0025.yaml; ledger: L-0003; introduced: rails-0.4.
- Exact instruction:

> Save objects that can load in a fresh Python interpreter using installed packages alone. Prefer built-in sklearn estimators, selectors and transformers. Never pickle locally defined estimators, functions or lambdas: they depend on an earlier script's __main__ and cannot be loaded reliably later. For an identity selector use an importable built-in passthrough transformer, not a custom wrapper. Switching to joblib does not restore missing definitions. Never fabricate replacement behavior to make an incompatible saved object load.

- Rationale: Saved custom objects could not load in subsequent scripts, and repairs repeated or concealed the serialization fault.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

## RL-0026

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; tasks: all.
- Source: RL-0026.yaml; ledger: L-0004; introduced: rails-0.5.
- Exact instruction:

> Persist the full row-preserving feature transformation contract, not just an estimator fitted after transient DataFrame mutations. Parsing, derived features, column selection and ordering needed later must be reproducible by the saved importable pipeline. Learned transforms fit only on the frozen training rows. Deterministic table preparation may precede the split only through a declared prepared-data artifact. Later steps pass the declared source feature schema to the saved pipeline, never assume derived columns already exist in a freshly loaded partition. Inspect fitted input names; do not invent missing columns or fit replacement preprocessing during evaluation.

- Rationale: A saved frontend expected derived inputs created only in an earlier script, so later feature selection could not reproduce its input schema.
- Evidence/before-after: see cited ledger and proposed/rails-0.3/DESIGN.md for observed versus anticipated basis; no isolated causal effect claimed.
- Genericity: task/library/workflow guidance; no dataset, column or provider name.

