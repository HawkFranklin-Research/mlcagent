# Workflow templates

Built-in templates are `tabular_classification` and `survival`. Both are marked DRAFT; review goals,
scientific methods, actions and thresholds before using them for revision evidence. The survival
runtime includes lifelines; its brief includes duration and event-indicator columns.

Each directory has template.yaml, events/*.yaml and actions/*.yaml. A template declares an ordered
event graph and allowed validation loops. Events declare entry gates, sub-goals with deterministic
checks, action catalogs, defaults and custom-instruction scope. Actions declare typed parameters,
input references, expected outputs, methods text and whether they may read test data.

Input references: registered_data (before split only), a named registered table, train, val,
prior_outputs and test (only in declared test-reading actions after explicit unlock). Output names
are relative to the action output directory. `prior_outputs` excludes raw-stage artifacts after split
and stale artifacts from invalidated workflow generations.

Available checks: event_done, fact_present, output_exists, artefact_hash_recorded, metric_present,
figure_count, split_frozen, fit_on_train_only, test_unlocked, user_confirm, study_fields_resolved and template_check.
An explicit user confirmation records a dated decision, not a model's assertion of scientific validity.
Facts must cite hashed, indexed artifacts; citation validation is not semantic fact verification.

Validate a template with `mlca templates validate PATH`; list with `mlca templates list`. These commands
are provided for the later validation phase. User templates reside in ~/.config/mlca/templates/.
Project initialization freezes template files and the source hash; subsequent edits require a new
project or a deliberately defined new protocol, not silent mutation of the old study.

Example action parameter: `seed: {type: integer, default: 42}`. Required outputs specify name, kind and
required. Unknown actions, unsafe output names, invalid defaults/checks and test reading outside the
allowed events are rejected. Optional checks.py functions run as trusted engine code, not sandboxed
model code. Review their implementation before installing a template.

## Writing content

Template content is the method MLCA guides a study through. Keep every field short, so that both the
models and the person reading the log get precise, comparable outputs.

| Field | Rule |
|---|---|
| `goal` | One sentence: what this event must establish. |
| sub-goal `text` | At most 10 words, phrased as the state reached ("Partitions hashed and test partition sealed"). |
| `custom_scope.description` | One sentence: what a custom instruction may do here, and the main thing it may not. |
| action `title` | At most 8 words; this is what the user sees as the option. |
| action `prompt` | Three lines, in this form: `Do:` (the computation, with concrete defaults), `Save:` (the exact required outputs), `Record:` (metrics and fact keys, each with its source output). Generic rules (inputs, fitting, test lock, no network) live in the Worker role prompt, not here. |
| `fact_candidates` | Only keys that a sub-goal, a later action or the report uses. |
| `methods_text` | One past-tense sentence for the generated methods draft. |
| `max_options` | 3 by default: fewer, more natural options. |

The Worker role prompt (`src/mlca/roles/prompts/worker_write.md`) adds an output contract to every action:
the required outputs plus at most one figure, summary tables (at most 50 rows and 12 columns, 4 significant
digits), at most 5 printed lines, and every important number recorded as a metric or a cited fact.

Concrete defaults in the v0.2.0 templates, to be reviewed for each study:
- classification: 60/20/20 stratified split with seed 42; logistic regression baseline and gradient-boosting
  alternative; primary metric ROC AUC; threshold by Youden's J on validation; 1,000-resample bootstrap CI on test;
- survival: 60/20/20 random split; Cox and penalised-Cox models; primary metric Harrell's C-index.

## Deferred study fields (content version 0.2.1)

The new built-in Onboard check requires an explicit main table, validated outcome columns and a row
meaning before progression. Initialization may leave columns unresolved. Human resolution is recorded
through Session.resolve_study; it resets Onboard generations/confirmations and preserves the original
brief. Single-table legacy projects retain compatibility; frozen historical templates are not edited.
Supporting tables are never implicitly merged and original inputs remain inaccessible after split.
See [native onboarding](native-onboarding.md).

## Autonomous problem types (work order 04 A2)

New initial templates cover regression (including multiple numeric targets), multiple
categorical outputs, clustering and representation learning. They retain the same
event graph, training-only fit evidence and final test lock. Regression defaults to
RMSE; multiple-output metrics are per-output and averaged. Clustering uses internal
metrics; representation uses reconstruction error. Scientific reliability is not
established by the scripted fixture tests.

Clustering may choose a generated entity-feature action for transaction tables.
This deterministic, non-fitted transformation becomes the analysis table before
the split; fitted transformations still belong after the split.

Evaluation-only columns are excluded at registration, before inventory and step
inputs. Hidden label values and source files are not copied into the project.
Unsupervised templates never fit a supervised probe. Required final per-row
Parquet artifacts contain source row IDs and partition names, plus assignments or
embeddings; they are local data artifacts, not LLM-readable summary tables.
Their populations must match the frozen training and test partitions. External
evaluation lives in the experiments repository and is labelled as researcher code.

## Autonomous problem types (work order 04)

In addition to classification and survival, the registry includes `regression`
(single or multiple numeric outcomes), `multilabel_classification` (multiple
categorical outcomes), `clustering`, and `representation`. They use the same
Session gates, train-only fit evidence and one-way test lock. A scripted synthetic
workflow checks each template through report; this is orchestration validation,
not evidence that a live model completes these methods reliably.

Clustering selects using internal metrics; representation uses reconstruction
error. `save_row_outputs` stores local-only Parquet assignments/embeddings with
`row_id` and `partition`. The engine checks uniqueness and membership of the
frozen train/test population. Hidden evaluation labels must be removed with
`--exclude-columns` before registration. ARI/NMI and a training-fitted linear
probe are computed afterward by the separate experiments evaluator, explicitly
not by the agent. Entity construction is an optional pre-split clustering action;
its checked output becomes the split input. It must preserve traceable row IDs.
