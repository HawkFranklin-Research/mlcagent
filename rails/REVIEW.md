# Rails review — rails-0.5 after batch-02

Review draft; no acceptance, ablation or freeze. All26 active rails are instructions; existing engine safeguards and contract fixes are separate. No held-out file was opened.

## Evidence and attribution

- Exploratory rounds1–2 used openrouter/free and are not compared numerically with the DeepSeek batches.
- Batch01 (rails03) completed0/12; its evidence and the infrastructure stop are experiments d792b50.
- Batch02 (rails04) completed3/12 with matching setup and clean external leakage checks: Heart, Abalone, Energy. Full evidence: experiments4a9a60d, bench/dev-loop/batch-02/{REPORT,REVIEW}.md and curated/MANIFEST.csv.
- Batch03 with rails05 has not started. Multiple rails/engine changes between batches prevent attributing aggregate improvements to one instruction.
- RL-0001 stays provisional; it requests concise setup output, not control over hidden reasoning.25 output-truncated calls in batch02 remain recorded.
- Anticipated rails retain their design-pass basis in proposed/rails-0.3/DESIGN.md; they are not relabelled as observed failures.

## RL-0001

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0001.yaml; ledger: L-0001; added in: rails-0.2.
- Exact instruction:

> During study-setup inference, give one concise proposal and a one-sentence justification. Include an alternative only for a concrete unresolved scientific ambiguity; otherwise return an empty alternatives list. Do not invent an unrelated prediction objective to populate the list.

- Rationale: Avoid unnecessary alternative proposals and excessive setup output before analysis can begin.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0002

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0002.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Choose problem_type from the schema. Two observed values in the outcome: binary. Three or more discrete labels: multiclass. Several categorical outcome columns describing the same row at different levels of detail: multilabel, with all of them as targets. One numeric measurement or count: regression. Two or more numeric outcomes recorded together: multioutput_regression. If no column is a plausible outcome, choose clustering when rows are entities or events to segment, and representation when the table is many homogeneous numeric features of one kind. Prefer the task the table was evidently assembled for over an incidental column.

- Rationale: Setup proposals chose a binary outcome as multiclass and a multi-output outcome set as a single target; the problem type decides every later step.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0003

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0003.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> List as leakage_suspects every column that is a component, sum, difference, rescaling or recoding of a target, or that is known only after the outcome (for example the raw score a binary target was derived from, or partial counts that add up to a total). List as identifier_suspects row keys, record numbers and codes with nearly one unique value per row. Never propose either kind as a feature.

- Rationale: A target reconstructed from its parts gives near-perfect scores without learning anything; setup is the only point where the agent names such columns before the split.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0004

- Kind: instruction; roles: navigator; events: onboard; problem types: all.
- Executable source: RL-0004.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Set group_column when a non-target column repeats across rows and identifies the source unit (subject, recording, customer, device), so its rows must stay in one partition. List time_columns when rows carry timestamps or calendar parts and the aim is to predict later periods. Leave both empty when no such column exists; do not invent them.

- Rationale: Rows from one source unit or one period on both sides of the split inflate validation and test scores; the split can respect them only if setup declares them.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0005

- Kind: instruction; roles: navigator; events: model, validate; problem types: all.
- Executable source: RL-0005.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Reach one complete, scored baseline before exploring. Try at most one alternative kind of model before freezing a candidate for test, and stop tuning once both have a recorded validation metric. Finishing the workflow comes before further optimisation.

- Rationale: Each extra model turn costs requests, time and new failure chances; the study measures completion of a valid workflow, not leaderboard performance.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0006

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0006.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Read outcomes and exclusions only from the _protocol JSON: targets in _protocol['targets'], dropped columns in _protocol['excluded_columns'], the group in _protocol['group_column'], task details in _protocol['task']. The Brief in this order is a different object; never index _protocol with Brief keys. If a needed key is missing, raise an error that lists the available top-level keys instead of guessing a nested path.

- Rationale: A model-step script failed with a KeyError after reading the protocol through keys that exist only in the Brief.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0007

- Kind: instruction; roles: worker; events: data, eda, split, preprocess, features, model, validate, test, interpret; problem types: all.
- Executable source: RL-0007.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Define the feature columns once: every column of the frozen table except the targets, the excluded columns and the group column, and except key-like columns: text codes or integer sequences whose values are all distinct and carry no measurement. Continuous measurements are never identifiers, however many distinct values they have. Use exactly that list in every step, and never let a target or excluded column reach a fitted transformer or model.

- Rationale: Feature lists rebuilt differently in each step let outcome-derived or key columns into models and break saved pipelines between steps.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0008

- Kind: instruction; roles: worker; events: preprocess; problem types: all.
- Executable source: RL-0008.yaml; ledger: L-0003; added in: rails-0.3.
- Exact instruction:

> Before fitting preprocessing, screen the candidate features on training rows without fitting a model. Exclude, in the saved preprocessing, only features that are confirmed derivations of a target: exact equality with it, or a row sum of up to three non-negative columns that equals it on every training row. Features with absolute correlation of 0.98 or more with a target are a warning, not proof: keep them and print one line with their names. Print one line naming any excluded feature and the reason. Correlation warnings apply only to numeric outcomes; never coerce categorical labels to floats for Pearson correlation. Skip that numeric screen for categorical outcomes and retain exact-derivation checks.

- Rationale: Setup sees only the schema, so leakage visible only in values must be caught on training rows; high correlation alone can be a legitimate strong predictor, so only exact derivations are removed.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0009

- Kind: instruction; roles: worker; events: preprocess, features, model; problem types: all.
- Executable source: RL-0009.yaml; ledger: L-0003; added in: rails-0.3.
- Exact instruction:

> Keep feature names through preprocessing. When the encoded output has at most 300 columns, call set_output(transform='pandas') on ColumnTransformer and Pipeline objects and use OneHotEncoder(handle_unknown='ignore', sparse_output=False). When it would be wider, keep sparse output inside one Pipeline that starts from the raw feature DataFrame, take names from get_feature_names_out(), and never pass that output to a transformer that selects columns by name. Use set_output only with components that support it; prefer built-in sklearn transformers with get_feature_names_out rather than custom components.

- Rationale: Transformers that output NumPy arrays lose column names and the next name-based transformer fails; dense output of very wide encodings exhausts memory on large tables.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0010

- Kind: instruction; roles: worker; events: preprocess; problem types: all.
- Executable source: RL-0010.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Before encoding, sort feature columns into types: numeric; low-cardinality categorical (one-hot); text or code columns with more unique values than 5% of rows (drop, or use a frequency encoding fitted on training rows, never one-hot); date or time strings (parse with pandas.to_datetime, derive numeric parts such as hour, day of week and month, then drop the raw string). Integer 0/1 indicator columns stay numeric.

- Rationale: One-hot encoding codes or raw timestamps creates thousands of columns, exhausts memory on large tables and memorises rows.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0011

- Kind: instruction; roles: worker; events: features, model, validate, test, interpret; problem types: all.
- Executable source: RL-0011.yaml; ledger: L-0003; added in: rails-0.3.
- Exact instruction:

> Saved transformers from earlier steps may already contain the earlier preprocessing. Before combining them, check isinstance(obj, Pipeline) and obj.named_steps to see whether the later object includes the earlier one; build on the most complete saved pipeline that accepts the raw feature DataFrame and append only the new estimator. Never place a saved pipeline after a step it already contains, and never pass NumPy arrays to a transformer that selects columns by name. Inspect feature_names_in_ for each loaded object and preserve its exact input columns and order. A saved selector may already wrap preprocessing: use that selector as the only frontend, or chain preprocessing once before a bare selector. Never feed derived or renamed columns back into a raw-column frontend.

- Rationale: Model steps chained a saved preprocessor before a saved selector that already contained it, applying preprocessing twice and failing on arrays.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0012

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0012.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Summary tables have one type per column: use NaN, not empty strings, for values that do not apply, or put numeric and categorical summaries in separate columns. Keep at most 50 rows and 12 columns; for wide summaries, place variables in rows and statistics in columns.

- Rationale: An EDA summary mixed empty strings into a numeric column and could not be saved.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0013

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0013.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Keep each script short and direct, about 120 lines or fewer: loop over columns instead of repeating blocks, no commented-out alternatives, no long docstrings, no restating of these instructions. A complete short script is better than an elaborate one that is cut off.

- Rationale: Worker responses exhausted the output allowance before the script was complete.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0014

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0014.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> When repairing, read the error type and message in the diagnostics first and change the smallest part of the script that causes it; keep the approach, inputs and outputs. A message about specifying columns with strings on non-dataframes means an array reached a name-based transformer (see RL-0009 and RL-0011). A KeyError on a JSON key means a guessed structure; use the keys the file has. Messages starting with 'MLCA:' state an engine rule; comply, do not work around it.

- Rationale: Repairs rewrote whole scripts and reintroduced the same fault in all three attempts.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0015

- Kind: instruction; roles: worker; events: all; problem types: all.
- Executable source: RL-0015.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> When the training table has more than 100000 rows, avoid methods whose cost grows with the square of the row count (full silhouette, kernel SVMs, pairwise distances, t-SNE, agglomerative clustering) and prefer linear models with saga or SGD solvers, HistGradientBoosting or MiniBatchKMeans. Every fit_record call still uses all training rows; compute expensive diagnostics that fit nothing on a fixed-seed subsample of at most 10000 rows and print its size.

- Rationale: Tables with hundreds of thousands of rows exceed sandbox time and memory with quadratic methods, and fit_record accepts only the full frozen training index.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0016

- Kind: instruction; roles: worker; events: model, validate; problem types: all.
- Executable source: RL-0016.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Tune only inside one fit_record call on the full training rows, with a search object (GridSearchCV or RandomizedSearchCV) whose folds respect the design; never call fit_record on fold subsets. If _protocol['group_column'] is set, use cv=GroupKFold and pass the training rows' group values through fit_record as groups=. If the task lists time columns, use cv=TimeSeriesSplit only when the frozen training rows are already in time order (never reorder them); otherwise skip internal folds and select on the validation partition. Do not use the group key as a feature.

- Rationale: Internal folds that ignore groups or time repeat the leakage the frozen split avoids, and fit_record accepts only the full frozen training index in its stored order.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0017

- Kind: instruction; roles: worker; events: model, validate, test; problem types: binary, multiclass.
- Executable source: RL-0017.yaml; ledger: L-0004; added in: rails-0.3.
- Exact instruction:

> For binary roc_auc, align the positive probability column with model.classes_ using the declared positive label, or model.classes_[1] when none is declared. Pass a binary indicator for that same label as y_true; roc_auc_score does not accept pos_label. Preserve the original labels for other metrics and record the positive-label convention. For roc_auc_ovr pass the full aligned probability matrix with labels=model.classes_, multi_class='ovr', average='macro'. When the smallest outcome category is under 10% of training rows, set class_weight='balanced' where supported.

- Rationale: Probability columns misaligned with labels silently invert or break ROC AUC; rare categories are otherwise ignored by default losses.
- Cause: batch02, Adult model: unsupported roc_auc_score pos_label keyword.
- Before/after: symptom preserved under rails04; rails05 outcome pending.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0018

- Kind: instruction; roles: worker; events: model, validate, test, interpret; problem types: multilabel.
- Executable source: RL-0018.yaml; ledger: L-0004; added in: rails-0.3.
- Exact instruction:

> Several categorical targets need MultiOutputClassifier or an estimator supporting multiple outputs, with the target DataFrame in _protocol['targets'] order. predict_proba returns one array per target. Do not pass a multiclass-multioutput matrix to a single-output metric. Compute f1_score(average='macro') separately on each target's one-dimensional true and predicted labels, then report the unweighted mean and per-target values. Both vectors must have the same native label type; an object array of encoded integers can be rejected as unknown. Preserve categorical labels directly, or save the training-fitted target encoders with the model and reuse their unchanged mappings. Never fit an encoder during validation or test.

- Rationale: Multi-output predictions have a different shape from single-output ones; metric code written for one target fails or scores only the first.
- Cause: batch02, Anuran validation: multiclass-multioutput/mixed-label scoring and attempted evaluation-time encoder fit.
- Before/after: symptom preserved under rails04; rails05 outcome pending.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0019

- Kind: instruction; roles: worker; events: model, validate, test, interpret; problem types: regression, multioutput_regression.
- Executable source: RL-0019.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Report every metric on the original scale of the targets. For non-negative counts or strongly right-skewed outcomes, prefer a Poisson loss or TransformedTargetRegressor with log1p and expm1, and invert before scoring. With several numeric targets, fit them together in _protocol['targets'] order (natively or with MultiOutputRegressor), and report the metric per target and their unweighted mean as the headline value.

- Rationale: Scores on a transformed scale are not comparable, and multi-output regression must keep target order between fitting and scoring.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0020

- Kind: instruction; roles: navigator, worker; events: eda; problem types: clustering.
- Executable source: RL-0020.yaml; ledger: L-0004; added in: rails-0.3.
- Exact instruction:

> If the proposed clustering units are entities but the input rows are repeated transactions, the Navigator must recommend build_entities before a distribution-only EDA action completes the event. In that entity-building step, before the split, the Worker builds one row per entity: drop rows without an entity key, handle reversing rows (negative amounts, returns) by an explicit rule printed in one line, and aggregate deterministically (recency against the last date in the table, frequency, total and mean value), with no fitted transform. Save the declared prepared-data artifact so the engine freezes the entity rows. Do not aggregate after partitioning or pretend transaction-level clustering satisfies an entity-level aim.

- Rationale: A distribution-only EDA completed before entity preparation, leaving missing group keys and the wrong analysis rows at the split.
- Cause: batch02, Retail chose distribution-only EDA, skipped existing entity preparation, then failed group splitting on missing entity keys. Its static-vs-temporal external criterion remains an author decision.
- Before/after: symptom preserved under rails04; rails05 outcome pending.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0021

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; problem types: clustering.
- Executable source: RL-0021.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> There is no outcome in this project: never treat any column as a label or count its categories as one. Choose the cluster count only from internal criteria (silhouette, Davies-Bouldin, Calinski-Harabasz, stability). Scale features before distance-based methods. Compute silhouette with sample_size at most 10000 and a fixed random_state. Required per-row outputs hold the assigned cluster for each row_id.

- Rationale: Template steps written for classification ask for an outcome; unsupervised projects must not invent one, and full silhouette is quadratic in rows.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0022

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; problem types: representation.
- Executable source: RL-0022.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> There is no outcome in this project: never treat any column as a label. Scale inputs to a common range fitted on training rows, and report reconstruction error in that scaled space, saying so. An autoencoder may be an MLPRegressor trained to reproduce its scaled input; its embedding is the middle hidden layer computed from coefs_ and intercepts_ without refitting. Record the embedding dimension. Required per-row outputs hold the embedding for each row_id.

- Rationale: Representation steps need a fitted encoder whose embeddings can be extracted without refitting, so that an external scorer can evaluate them.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0023

- Kind: instruction; roles: worker; events: data, eda, preprocess; problem types: all.
- Executable source: RL-0023.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Check text columns for placeholder tokens that stand for missing values (a lone '?', '-', 'NA', 'N/A', or whitespace-only strings) and for surrounding whitespace. Strip whitespace and convert only such placeholders to missing inside the fitted preprocessing, and print one line naming the placeholders found and how many columns contain them.

- Rationale: Published tables mark missing values with placeholder strings; left as text they become spurious categories and hide the true amount of missing data.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0024

- Kind: instruction; roles: worker; events: preprocess; problem types: clustering, representation.
- Executable source: RL-0024.yaml; ledger: L-0002; added in: rails-0.3.
- Exact instruction:

> Apply log1p to heavy-tailed non-negative features (such as monetary totals and counts) inside the fitted preprocessing, before scaling.

- Rationale: Heavy tails let a few extreme rows dominate distance- and reconstruction-based methods.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0025

- Kind: instruction; roles: worker; events: preprocess, features, model; problem types: all.
- Executable source: RL-0025.yaml; ledger: L-0003; added in: rails-0.4.
- Exact instruction:

> Save objects that can load in a fresh Python interpreter using installed packages alone. Prefer built-in sklearn estimators, selectors and transformers. Never pickle locally defined estimators, functions or lambdas: they depend on an earlier script's __main__ and cannot be loaded reliably later. For an identity selector use an importable built-in passthrough transformer, not a custom wrapper. Switching to joblib does not restore missing definitions. Never fabricate replacement behavior to make an incompatible saved object load.

- Rationale: Saved custom objects could not load in subsequent scripts, and repairs repeated or concealed the serialization fault.
- Cause/basis: the cited ledger and individual design-pass entry (observed versus anticipated kept separate).
- Before/after: retained unchanged in rails05; batches01–02 provide aggregate evidence only, not an isolated effect estimate.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## RL-0026

- Kind: instruction; roles: worker; events: preprocess, features, model, validate, test, interpret; problem types: all.
- Executable source: RL-0026.yaml; ledger: L-0004; added in: rails-0.5.
- Exact instruction:

> Persist the full row-preserving feature transformation contract, not just an estimator fitted after transient DataFrame mutations. Parsing, derived features, column selection and ordering needed later must be reproducible by the saved importable pipeline. Learned transforms fit only on the frozen training rows. Deterministic table preparation may precede the split only through a declared prepared-data artifact. Later steps pass the declared source feature schema to the saved pipeline, never assume derived columns already exist in a freshly loaded partition. Inspect fitted input names; do not invent missing columns or fit replacement preprocessing during evaluation.

- Rationale: A saved frontend expected derived inputs created only in an earlier script, so later feature selection could not reproduce its input schema.
- Cause: batch02, Bike feature step: frontend required transient date-derived columns absent from the next input.
- Before/after: symptom preserved under rails04; rails05 outcome pending.
- Genericity: concerns task type, library interfaces, analysis units or workflow contracts; no development dataset/column or provider/model identifier occurs in the instruction.

## Engine fixes are not rails

B-0001–B-0013 remain in LEDGER.md with original evidence. B-0014–B-0016 (43b7407) align per-row audit artifacts with the runtime, make classification primary-metric instructions task-aware and add fixed value-free scoring diagnostics. Forty focused regressions passed; full consolidated gate pending. Checks are not relaxed and no failed Worker script is replaced.

## Rejected shortcuts

- Injecting manifest targets, expected groups/time fields or known leakage columns into the agent.
- Aliasing binary roc_auc and multiclass roc_auc_ovr merely to satisfy a check.
- Allowing CSV/raw-row egress or skipping row_id/partition validation for audit outputs.
- Refitting encoders or replacement preprocessing on validation/test rows.
- Padding or substituting frozen training rows to make entity aggregation fit.
- Replacing failed scripts with a no-AI/reference analysis.
- Changing Retail researcher expectations without the author, or treating incomplete fits as a completed final study.

All earlier exact instruction versions remain in local Git history. AcceptanceK3, rails ablation and author review remain pending.
