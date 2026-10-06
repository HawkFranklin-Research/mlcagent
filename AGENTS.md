# MLCA implementation instructions

Read plan.md and docs/DECISIONS.md before editing. Implement P0–P8; P9 requires a separate request.
All code is new. Reference repositories, legacy data and the paper repository are read-only.
Use the plan's neutral vocabulary. Enforce policies in code; describe enforcement limits accurately.
Models are configured, not hard-coded. Credentials come only from environment variables.
Do not inspect credential files or record secrets. Add notices for any copied material.
The author has deferred tests, smoke runs, model calls and full-cycle validation. Do not add or run tests
until requested. Source formatting and static inspection are permitted; never label them runtime validation.
Commit locally per implementation phase; no remote, publishing or pushing without authorization.
Keep CHANGELOG.md and docs/DECISIONS.md current. Draft workflow content requires author review.
Future validation commands: uv run pytest; uv run ruff check; uv run mlca doctor.
