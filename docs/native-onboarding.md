# Native onboarding and model settings

These changes are on `native-onboarding`; the browser plans and frozen master are unchanged.

## Create a study

Use **Browse** for the project folder or data file/folder, or type a path (also works over SSH). The picker permits creating a new project folder beneath an existing parent. Supported study inputs remain CSV, TSV and Parquet; folder selection does not imply support for Excel, images or arbitrary file formats.

**Find tables** scans recursively, excluding hidden/cache directories and symlinks. Choose the main study table explicitly when there is more than one. Supporting tables are optional and unchecked by default. Files are never concatenated or joined automatically. Each selected file is registered with its own checksum; the split and replay use the main table. Existing rules prevent reading original registered inputs after split freezing, including supporting files.

Choose a workflow using its friendly title. Classification asks for the column to predict; survival asks separately for duration and the event indicator (1 observed, 0 censored). Choose **I'll decide later** if uncertain. Explain what one row means when known; it is not automatically assumed to be one independent sample. The repeated-subject answer records context; MLCA does not infer subject IDs or automatically select a group split.

During Onboard press **d — Study details** to resolve the table, outcome columns and row meaning. Column mappings are validated against the selected table. Saving details records an attributed event, resets current Onboard checks/confirmations and invalidates the previous brief step generation. Record the updated brief and confirm it again before proceeding. The original brief answers remain in the log and `original_brief` state. Mappings cannot be changed after leaving Onboard or freezing a split; branch at an appropriate earlier point or create a new project.

CLI examples:

```sh
mlca init /path/to/project --data /path/to/folder --primary-data table_name
mlca --project /path/to/project study --target Result --unit patient
mlca --project /path/to/project study --duration duration --event-column observed --unit patient
```

`--primary-data` accepts a registered table name or an exact selected file path. Noninteractive invalid names remain errors; blank target/duration/event choices are deferred. The existing MCP `mlca_init` tool accepts the optional `primary_data` field, with no additional tool. An MCP agent cannot resolve/confirm these human study decisions itself; use the native CLI/TUI. Task cards may provide `primary_data` for reproducible automated policy runs.

## Configure models

Open model settings with **s**. Provider choices are OpenRouter, OpenAI and local/OpenAI-compatible servers. Endpoints and ordinary environment-variable names are supplied automatically; custom endpoints remain editable. Use one provider/model for both roles or choose separate Navigator and Worker settings. Existing unrelated providers, optional roles, generation settings and sandbox settings are preserved.

Credentials can come from the environment or be pasted into a masked field. Pasted keys stay in this application process only. Config YAML stores a non-secret session reference, not the key; restarting requires pasting the key again. **Forget pasted keys** clears these references from memory (it does not remove environment credentials). Redaction covers session keys, and analysis subprocesses receive a separate scrubbed environment. There is no plaintext key file. Author-approved OpenRouter sign-in can instead remember an OAuth key in the secure OS keyring; see [OpenRouter sign-in](providers.md#openrouter-sign-in-native-driver-mode).

Type any model ID directly, or browse cached models. **Refresh** explicitly requests the provider's `/models` catalogue with the configured key, sending no study data and making no completion request. Pasted keys are unavailable to a separate CLI/bench process; use environment variables or a securely remembered OpenRouter sign-in for those runs. Catalogue results are cached for offline use and labelled stale after 24 hours. Search by name/ID and optionally filter zero-priced models. Free availability, quotas, structured-output compatibility and code quality are not guaranteed. No fallback silently switches to another model.

Catalogue token pricing is recorded with a source and fetch timestamp. Unknown or non-token fees require an explicit per-request USD bound. Session/turn limits stay enforced. Saving settings does not run a paid model test. Connection/generation smoke calls remain author-enabled future checks.

## Verification and limits

Offline unit, TUI and integration regressions cover supported-folder discovery, duplicate stems, deferred mappings/gates, replay, provider preservation, masked/session credentials, catalogue failures/cache/free filtering and pricing. The existing synthetic suite exercises execution and scientific guard rails. No live providers or original scientific datasets are run merely for onboarding validation.

Native file selection is a terminal picker, not an operating-system graphical dialog. Unsupported modalities and multi-table joins require a separate workflow design.

## Local installation

Installing a local source folder with uv copies it into the tool environment. After changing branches
or pulling new source, refresh the installed tool explicitly:

```sh
uv tool install --force /home/prime/Documents/github/mlca-paper-codebases/mlca-revized
mlca --version
```

The unpublished development code retains version 0.2.0b1; record the branch and Git commit when
comparing behavior. The published PyPI beta and frozen master are not replaced by these source edits.

### Validation result (12 October 2026)

Final full offline suite: 152 passed, 1 skipped (PowerShell unavailable), 619.88 seconds. Ruff lint and
format checks pass. Forms were exported and visually inspected; deferred Study details selection/save
passed. No real model calls or original-data studies were run. New resolution records require updated
native source; the old PyPI beta cannot interpret the new record type.

Installed-source checks: local uv tool refresh succeeded; mlca --version, installed-template resources,
headless new forms and mlca mcp doctor (14 tools) passed. A final UI-only blank-path guard prevents
empty data input from registering the current directory implicitly; the post-guard focused suite
passed 24 tests in 6.96 s. The full 152-pass/1-skip result above precedes that UI-only hardening.

## Restart after a failed attempt

If **Create study** selects a folder already containing `.mlca`, MLCA offers **Open existing
study**, **Create fresh study in a new subfolder**, or **Cancel**. The fresh option retains your
new-study form and creates the first unused `study-NNN` folder within the selected folder.
Earlier data, results and logs are preserved; no reset deletes them. A partial initialization
without `project.yaml` cannot be opened, but can still be followed by a fresh study. Opening an
existing project continues its recorded state; it does not apply the new-study form.

CLI initialization still refuses to overwrite an existing attempt. Choose a new `mlca init` path
for a fresh CLI study, or use `mlca -p <existing-folder>` to open the existing project.
