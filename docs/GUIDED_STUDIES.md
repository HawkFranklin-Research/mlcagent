# Guided studies and the no-AI comparison arm

New studies use template version 0.3.0. Existing studies retain their frozen template and runtime.

## Guided controls

Open a project with `mlca -p <project>`. `a` runs or resumes autopilot; Space pauses after the current step. Autopilot stops for questions, the brief approval, validation-model approval, test authorization, failures or budget exhaustion. Numbered cards and custom instructions remain available in step mode. `p` opens pending approval requests.

Questions dock in the main screen. Left/right select a question or Review; choose an answer and press Answer. Esc uses the recommendation only for non-sensitive questions. Leakage, outcome selection and label merging require explicit answers. Free text is mapped to a listed answer and requires a separate confirmation. Without a model, select a listed answer directly.

CLI equivalents:

```bash
mlca -p <project> turn
mlca -p <project> autopilot
mlca -p <project> questions
mlca -p <project> questions answer <question-id> 0
```

Answer indexes are zero-based. MCP adds `mlca_questions` and `mlca_answer` (16 tools total). Human-only questions cannot be answered by an agent principal. The human uses the CLI/TUI; client permission restrictions still apply. MCP menus expose the situation and pending questions. Brain mode makes no MLCA model calls.

## Generic data review

Before splitting, deterministic rules examine labels, possible outcome aliases/sources, identifiers, missingness, grouping, duplicates and survival coding. These are hints, not proof of the absence of leakage. The author must review sensitive recommendations. Raw files remain unchanged. Decisions produce a separate, hashed prepared table in its source format and an immutable protocol input. Group columns assign partitions but do not enter prediction features. Methods and the event log retain the decisions and actors.

Task type and primary metric are recorded after the decisions: binary ROC AUC, multiclass macro one-vs-rest ROC AUC, or survival C-index. Worker work orders include the same task and exclusions. Model/feature fits still require the exact frozen training index; the test exposure guard is unchanged.

## Explicit reference comparison

The default is `worker`: its code is written by the Worker. A Worker failure stays recorded; reference code is never used for recovery.

Create a separate comparison study:

```bash
mlca init <new-project> --data <table.csv> --brief-file <brief.yaml> \
  --template tabular_classification --measurement-arm reference
mlca -p <new-project>
```

For survival use `--template survival` and specify duration/event columns in the brief. The reference arm is driver-only. It makes no model calls, even if global model roles are configured. Its immutable project record, step scripts, snapshots, benchmark manifests and metrics name `measurement_arm: reference`. Changing an existing study's arm is refused. Reference code is included in the frozen runtime and runs through the same sandbox, hashes, manifests and fit checks. Level A remains the default; level B requires explicit opt-in.

Reference primary steps audit schema, summarise distributions, fit imputation/encoding/scaling, retain or filter features, fit both prespecified models, select on validation, test once with 1,000 bootstrap resamples, and calculate validation permutation importance. Logistic regression and class-balanced histogram gradient boosting cover binary/multiclass classification; Cox and penalised Cox cover survival. Cox proportional-hazards diagnostics use training rows. Fits/convergence failures remain failures; no alternate family is silently substituted. The reference arm supports primary catalogue actions, not arbitrary custom code or optional supporting actions.

`mlca bench` task cards can set `measurement_arm: reference` and `guided: true`. Approvals and recommended answers executed by task-card policy are recorded as `user:policy/<hash>`, never as human decisions. Reference comparisons and Worker runs must be reported separately.

## Offline acceptance

`scripts/acceptance_run.py` drives the actual Textual app headlessly, presses Run, answers docked questions and approves the three human cards under an explicit policy. It reads the six benchmark tables outside this repository and preserves every failed run in a fresh output directory. It writes task-card hashes, stop lists, metrics and `summary.csv`; no raw data enter Git. This is functional acceptance, not a published experiment or evidence of live Worker reliability.

```bash
uv run python scripts/acceptance_run.py \
  --data ../benchmark_datasets \
  --out /absolute/path/to/new-acceptance-directory
```

Live Worker acceptance remains separately authorized. Never replace its failed scripts with reference scripts.
