# Changelog

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
