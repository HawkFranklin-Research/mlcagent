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
figure_count, split_frozen, fit_on_train_only, test_unlocked, user_confirm and template_check.
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
