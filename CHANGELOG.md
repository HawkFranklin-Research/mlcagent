# Changelog

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
