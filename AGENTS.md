# MLCA implementation instructions

Read plan.md and docs/DECISIONS.md before editing. Implement P0–P8; P9 requires a separate request.
All code is new. Reference repositories, legacy data and the paper repository are read-only.
Use the plan's neutral vocabulary. Enforce policies in code; describe enforcement limits accurately.
Models are configured, not hard-coded. Credentials come only from environment variables.
Do not inspect credential files or record secrets. Add notices for any copied material.
Prompt 01 authorizes and requires permanent offline tests, including slow synthetic integration and TUI runs.
Real model calls and original-data scientific runs remain deferred. Do not mislabel static checks as runtime validation.
Commit locally per implementation phase; no remote, publishing or pushing without authorization.
Keep CHANGELOG.md and docs/DECISIONS.md current. Draft workflow content requires author review.
Future validation commands: uv run pytest; uv run ruff check; uv run mlca doctor.

Never place caches or virtual environments other than `.venv/` inside the repository.
