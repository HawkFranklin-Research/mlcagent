# Prompt 01: functional fixes after the external review (6 October 2026)

You are the coding agent for MLCA v2 in `/home/prime/Documents/github/mlca-paper-codebases/mlca-revized/`.
Read `plan.md` (sections 0, 3, 6, 7, 13) and `AGENTS.md` first. Every rule there still applies.

This prompt is the author's instruction. It **authorises and requires a permanent test suite** for the work
below; the earlier "tests deferred" decision no longer applies to these items. Record that change in
`docs/DECISIONS.md`.

## 0. Start state

- An external reviewer drove a full synthetic project offline (fake provider, Linux sandbox level A) after
  the two startup fixes. Init, all 11 events, the test lock, `replay --verify`, reports, branching and tamper
  detection worked. The bugs below were found in that run.
- Uncommitted work by the reviewer is in the tree: the logo and banner (`assets/logo*.{txt,png}`,
  `scripts/make_logo.py`, `src/mlca/tui/banner.py`, welcome/main screen and CLI changes, CHANGELOG and
  DECISIONS entries) and `docs/prompts/`. **First step:** run `uvx ruff check src scripts` and a headless
  TUI start. Then commit that work alone: `Add MLCA logo, compact banner and agent prompts`. Do not rewrite it.
- Reviewer fixtures to build the tests on: `docs/prompts/fixtures/make_synthetic.py` (400-row table),
  `synthetic_brief.yaml`, and `synthetic_fake_llm.yaml` (fake Worker scripts for every default action, plus
  one scope answer). With these, the default path runs from `onboard` to `report` with:
  - a user confirmation in `onboard` (`brief_confirmed`) and in `validate` (`model_selected`);
  - `mlca unlock-test --phrase "UNLOCK TEST"` in `test`.

  Move or copy the fixtures to `tests/fixtures/`.

## 1. Fixes (each with the test named in its "Test" line)

### F3: alternative actions can complete their event
**Problem.** Each event's "required output" sub-goal uses `output_exists` with a single `action`, always
the default one. Choosing the other action in an event can never complete it. In `split`, choosing
`freeze_group` is a dead end, because the split cannot be frozen twice on a branch.

**Change.**
1. In `src/mlca/engine/checks.py`, extend `output_exists` to accept either the current form
   `{action, output}` or an any-of form:
   ```yaml
   check:
     type: output_exists
     any_of:
       - {action: freeze_stratified, output: split.json}
       - {action: freeze_group, output: split.json}
   ```
   Pass if any listed (action, output) exists in a completed, current-generation step. Keep the old form
   working.
2. In `src/mlca/templates/model.py`, add an optional field on actions, `role: primary | supporting`
   (default `primary`).
3. In `src/mlca/templates/loader.py`, add validator rules:
   - every `primary` action of an event must appear in at least one sub-goal check of that event (in
     `action` or `any_of`);
   - `supporting` actions must not;
   - the error names the event file and the action.
4. Update **both** templates (`tabular_classification`, `survival`). Make the alternatives primary and list
   them in `any_of`:
   - `split`: both freeze actions;
   - `features`: select + retain;
   - `model`: the two train actions.

   Mark the purely descriptive actions `supporting`:
   - `count_target`, `plot_missingness`, `audit_preprocessing`, `audit_validation`, `audit_test`,
     `plot_results`;
   - and their survival equivalents.

   Template *content* stays DRAFT for the author. Only this structure changes.
5. Remove the duplicated `fact_candidates` copied from `audit_schema` into `count_target` (both
   templates).

**Test.**
- Unit: `output_exists` with `any_of`, for both pass and fail.
- Loader: rejects an event whose primary action is not in any check.
- Integration: a run that chooses `freeze_group` (synthetic data with a `group` column added) completes
  `split`.
- Integration: a run that trains `train_alternative` only completes `model`.

### F4: branches resume correctly
**Problem.** `Session.branch()` / `checkout()` do not re-run checks, so a branch created at a completed step
shows unfinished sub-goals. The fallback option list is then empty, because the duplicate filter removes
the already-completed default action, and only "custom" is offered.

**Change.**
1. In `src/mlca/api.py`, call `checks.run_all(...)` after `branches.create(...)` and after
   `branches.checkout(...)`, then `materialise`.
2. In `src/mlca/engine/options.py`, rewrite `fallback()`:
   - start from `default_options`, then add the event's other **primary** actions not yet completed with
     the same parameters in the current generation, up to `max_options`;
   - if the event is done, return no action options; the engine adds `next`.
3. Always return a non-empty list while the event is open. If every action is exhausted, return the
   primary actions again with a `why_now` saying "Repeat with different parameters" for actions that have
   parameters. Return none for parameterless ones, and in that case `options()` adds a one-line note to
   the response explaining that the event needs a custom instruction or a branch.

**Test.**
- Branch from the completed `07_model_*` step: the status shows `model` sub-goals re-checked, and the
  options include `train_alternative`.
- `checkout main` restores main's state.

### F5: the target column is validated, not free text
**Problem.** `engine/split.py:83` and `runner/verify.py:57` use `state.brief.get("target")`, the
verbatim free-text answer. An answer like "the Result column" breaks the split.

**Change.**
1. In `src/mlca/project/init.py`, after the inventory, resolve the target against the registered
   table's columns:
   - exact match first, then case-insensitive unique match;
   - interactive CLI or TUI: if unresolved, show the column list and ask the user to pick one;
   - non-interactive (`--brief-file`): fail with a message listing the columns.
2. Store the result in the `BriefRecorded` payload as a separate structured field,
   `{"answers": {...verbatim...}, "columns": {"target": "<column>"}}`. The verbatim answers stay untouched.
3. For the survival template, also resolve `duration` and `event_column` the same way.
4. Add `ProjectState.columns` in `log/replay.py`. Make `split.py`, `verify.py` and any other reader use
   `state.columns["target"]`. Old projects without `columns` fall back to the verbatim answer only if it
   is an exact column name; otherwise raise a clear error.
5. Show the resolved columns in the `onboard` step output and the TUI facts panel, so the
   `brief_confirmed` user confirmation covers them.

**Test.**
- Init with target "Y" on a column "y" resolves to `y`.
- Init with "the y column" non-interactive fails and lists the columns.
- The split uses the structured field.

### F6: event-log noise and read cost
**Problem.** Every CLI call writes `SessionStarted`, giving 244 records for 13 steps. Every `state` access
re-reads, re-parses and re-hashes the whole log, and `emit()` calls `state`, so a long project gets
quadratically slower.

**Change.**
1. **Lazy session records.** `Session.__init__` no longer writes. `emit()` writes `SessionStarted` just
   before the first record of that session. `close()` writes `SessionEnded` only if the session started.
   Read-only commands (`status` without `--recheck`, `log`, `usage`, `branches`, `templates`, `doctor`)
   write nothing.
2. **Incremental store** (`src/mlca/log/store.py`):
   - cache the parsed records, the byte offset and the last line hash per `Store` instance;
   - on `read()`, if the file size equals the cached offset and `head.json` matches, return the cache;
   - if the file grew, parse and verify only the new bytes; the first new record's `prev_hash` must equal
     the cached last hash;
   - if the file shrank or anything mismatches, do a full verify, which raises on corruption;
   - `log --verify` and `Session.open` always do a full verify.
3. **State cache** (`api.py`): cache `replay(...)` keyed by (branch, head record id); invalidate on append.

**Test.**
- A sequence of read-only commands leaves the record count unchanged.
- 5,000 synthetic appends through `Store.append` complete in a bounded time (assert < 30 s on this
  machine; print the time).
- After an incremental read, editing an earlier line is still caught by `log --verify` and by a new
  `Session.open`.

### F7: small items
1. **Tamper message names the edited line.** In `store._read`, when record N's `prev_hash` does not match
   the hash of line N−1, the message must say:
   `line N−1 was modified (its hash no longer matches line N)`.
   When only the last line was edited (`head.json` mismatch), it must say `last line (L) was modified or
   truncated`.
   Test both.
2. **Key bindings.** `ctrl+i` is Tab in terminals and `ctrl+s` is XOFF in some.
   - Move the welcome-screen actions to screen-level bindings `o` (open), `i` (init), `s` (configure),
     `q` (quit).
   - Move the workflow bindings (`1`–`4`, `n`, `l`, `c`, `f`, `b`, `r`, `u`, `v`, `t`) from the App to
     `MainScreen`, so the welcome footer no longer shows "Choose an option".

   Test with a Textual pilot that the welcome footer lists only its four keys.
3. **Log stream text.** The main screen's log stream currently prints raw option dicts
   (`[{"id": "custom", ...}]`). Print readable lines, e.g. `options: 1 Audit schema · custom`, and the
   record type plus a short summary for each subscribed record.
4. **Orphan step folders.** `runner/run_step.py` creates the step folder before `inputs_for()` validation,
   so a refused step leaves an empty folder. Validate inputs first, then create the folder.
5. **uv cache inside the repo.** `.cache/` (about 347 MB of uv cache) sits in the repository folder.
   - Confirm it contains only `uv/`, then delete it.
   - Make sure no script sets `UV_CACHE_DIR` inside the repo.
   - Add one line to `AGENTS.md`: "Never place caches or virtual environments other than `.venv/` inside
     the repository."

## 2. Strictness: keep it, make it understandable

The author keeps these strict rules. Do **not** relax them. Make the refusals explain themselves:
- In `preprocess`, `features` and `model`, every step (including custom) must fit through
  `mlca_runtime.fit_record`. When a custom instruction there fails that static check, the message to the
  user must say: "Steps in this event must fit on the training partition with fit_record. For read-only
  inspection, use the validate or interpret event."
- `fit_record` requires the exact frozen training index. On mismatch, the error must name the expected
  and received row counts.
- Add both rules, with their reasons, to `docs/security-model.md` (a short "Scientific guard rails"
  section) and to `README.md`.

## 3. Test suite (permanent)

Create:
```
tests/
  conftest.py                 tmp project factory; XDG_CONFIG_HOME/XDG_DATA_HOME in tmp; fake provider config
  fixtures/                   reviewer fixtures (section 0) + variants (group column, survival synthetic)
  unit/test_store.py          hash chain, incremental read, tamper messages (F6, F7.1)
  unit/test_checks.py         output_exists any_of (F3)
  unit/test_template_loader.py  primary/supporting validation (F3)
  unit/test_options.py        fallback behaviour (F4)
  unit/test_init_columns.py   target resolution (F5)
  integration/test_default_path.py   full synthetic run onboard→report; replay --verify; reports; usage==egress lines
  integration/test_alternatives.py   freeze_group and train_alternative paths (F3)
  integration/test_branching.py      branch at model step, checkout main (F4)
  integration/test_sandbox.py        (skip if no bwrap) a probe script cannot read the original data, vault or key dir; network blocked
  integration/test_test_lock.py      score_test refused before unlock; plaintext removed after; loop refused after unlock
  tui/test_tui.py                    Textual pilot: welcome renders banner, footer keys; main screen opens a project; q quits
```

- Mark slow environment-creating tests `@pytest.mark.slow`, but **run them** here.
- `uv run pytest -q` must pass offline.
- Put the command and its pass/fail counts in `docs/IMPLEMENTATION_STATUS.md`, replacing "Deferred" in
  the rows these tests cover.

## 4. Done when

- `uvx ruff check src scripts tests` and `uvx ruff format --check` pass, and `uv run pytest -q` passes
  (paste the summary line in the final message).
- Every F-item has its test, and each test fails if its fix is reverted. Spot-check F3 and F6 by reverting
  them locally and quoting the failure; restore afterwards.
- `CHANGELOG.md` has a section "Functional fixes after review" and `docs/DECISIONS.md` records the
  decisions above.
- Commits are local only, one per F-item plus one for the tests. No remote, no push, no publishing.
- The final message lists what changed, the test summary, anything not done, and why.
