# Changelog

## Logo and banner — 6 October 2026
- Author-provided logo stored as `assets/logo_source.png`; `scripts/make_logo.py` (dev-only: pillow, numpy)
  generates `assets/logo.txt` (36x10 Braille art of the figure) and `assets/logo.png` (512x512 grayscale).
- New `mlca/tui/banner.py`: compact banner (logo, two-row wordmark, tagline, version, project path), a
  wordmark-only form below 84 columns, and a one-line brand bar.
- Welcome screen shows the banner centred; main screen shows the brand bar instead of the Textual header.
- `mlca init` (interactive) and `mlca doctor` (human output) print the banner on a terminal only; JSON and
  piped output are unchanged.
- Checked: ruff, package build includes the assets, headless TUI welcome (110 and 70 columns) and main screen.

## Startup corrections — 6 October 2026
- Defer branch annotations so the `list` method does not shadow the built-in annotation type at import.
- Rename TUI helpers to `_can_act` and `run_session_action`, preserving Textual's startup and action dispatcher methods.
- CLI help/version and headless welcome-screen startup, guarded actions and keyboard quit checks pass.
- Full-cycle, provider, scientific and broader UI validation remain deferred.

## P0 — Repository bootstrap
- Package, build configuration, agent rules and decision log created.
- Validation deferred by author; no tests or runtime checks performed.

## P1 — Event log and state
- Payload schemas, durable hash-chained append, head checkpoint, pure replay and branch ancestry implemented.
- Runtime validation deferred.

## P2 — Template model and deterministic checks
- Declarative schemas, validation, gates and deterministic sub-goal checks implemented.
- Draft template content follows in this phase. Validation deferred.

## P3 — Project lifecycle
- Read-only data registration and inventory, frozen workflow snapshots, separate uv analysis environments,
  runtime evidence helpers and edit-aware materialised views implemented. Runtime validation deferred.

## P4 — Execution and test lock
- Standalone subprocess lifecycle, static checks, Linux namespace mounts, explicit weaker fallback,
  engine-managed split and encrypted test vault implemented. Runtime validation deferred.

## P5 — Providers and request evidence
- Configured SDK adapters, fake response scripts, bounded retries, structured responses and conservative
  request budgets implemented. Transactional request envelopes produce usage/egress ledger views.
- Real requests, provider smoke checks and offline tests remain deferred.

## P6 — Guided turn loop and headless interface
- Navigator/Worker roles, prompt files, validated options, scoped custom actions, bounded repairs,
  fact citations, Session API and CLI implemented. Script reproduction is an explicit command.
- No end-to-end, smoke or real-provider execution performed.

## P7 — Terminal interface and reports
- Textual project/configuration forms, event graph, options, sub-goals, facts, streaming execution log,
  branch controls and explicit test unlocking implemented.
- Deterministic methods/provenance/figure/usage reports and optional Inspector added.
- Original text banner only; image-logo decision remains pending. Runtime/UI validation deferred.

## P8 — Survival workflow and hardening
- Survival template, event generations, loop invalidation and project-wide test-exposure controls added.
- Stale artifact/confirmation reuse, branch environment-lock mismatch and user-edited views are guarded.
- Source formatted and linted; architecture, security, provider/template guides and status documented.
- Tests, smoke runs and scientific/live validation remain deferred by the author.

## Functional fixes after review
- F3: any-of required-output checks and validated primary/supporting action roles in both templates.
- F4: re-check branch/checkout sub-goals and offer remaining primary fallback actions with exhaustion notes.
- F5: validate and persist structured target/survival columns while preserving verbatim brief answers.
- F6: lazy session records, incremental verified log reads and cached branch-head project replay.
- F7: screen-specific keys, readable TUI logs, orphan-folder prevention, precise tamper/refusal messages
  and removal of the repository-local uv cache. Fit index checks retain exact-index enforcement.
- Permanent offline regression suite: 40 passing tests, including slow synthetic classification paths,
  fresh script replay, branch recovery, test-lock lifecycle, namespace denial and headless TUI behavior.
- F3/F6 revert checks fail as expected; numerical threads and external test scratch keep runs bounded.

## Distribution preparation
- A: dynamic version metadata, verified wheel resources, optional loopback browser TUI and clean-home
  uv-tool installation checks. The source artwork is excluded from wheels.
