# Rails ledger

## Baseline: rails-0.0

The prompts, templates and engine checks at ad92ebd form the historical baseline.
No historical prompt has been moved into an instruction rail. Fresh development entries follow below. The prior Nemotron batch remains development
evidence, not a frozen evaluation. New entries must identify the run, actual model,
event, step, category, value-free diagnosis, files, commit and fresh verification.


## B-0001 — 16 October 2026 — engine setup-contract and accounting fix

- Evidence: `../mlcagent-experiments/bench/dev-loop/round-01/REVIEW.md` and
  `round.json`; original setup request/response envelopes are kept under each
  table and hashed in `setup-evidence/MANIFEST.csv`.
- Eleven setup failures, before any project/Worker step: breast_cancer_diagnostic,
  heart_disease_cleveland, abalone, energy_efficiency, seeds, dry_bean,
  optical_digits, adult, anuran_calls, bike_sharing_hourly, online_retail.
- Actual model mix: Nemotron nano/super/lightning, Dots preview, Laguna and
  Cohere North (exact provider IDs in round.json). Event: onboard; step: none;
  original categories: invalid_inference or runtime_error:ValidationError.
- Value-free error: inference passed the advertised schema but failed a later
  hidden constraint (metric identifier, incomplete alternative or task cardinality).
- Diagnosis: engine response schema and semantic validation were inconsistent.
  No scientific rule is weakened. Advertise complete nonrecursive alternatives
  and allowed metric identifiers, and validate local table constraints inside
  the existing one-repair structured path. Local validation context is never
  included in the provider request.
- Accounting: preserve known request/tokens/cost/latency/model distribution when
  setup fails before a project exists. Unknown compute time stays unavailable.
- Files: autonomous/inference.py, autonomous/runner.py, llm/structured.py,
  evaluation/bench.py; regressions: integration/test_setup_contract.py.
- Rails set after engine fix: rails-0.1. Commit: recorded after local commit in
  the review package (resolve via git history for this entry).
- Verification: synthetic invalid metric, incomplete alternative, unknown-column
  and task-cardinality responses repair once or fail with invalid_inference;
  zero raw-row context sent. Fresh live verification pending.

## L-0001 — 16 October 2026 — RL-0001 (instruction)

- Evidence: `../mlcagent-experiments/bench/dev-loop/round-01/covertype/setup-001/`;
  hashed copies in round-01/setup-evidence/covertype/setup-001/.
- Actual model: poolside/laguna-s-2.1:free. Event: onboard; step: none;
  failure category: output_truncated. A 16,384-token output allocation was
  exhausted before a usable study proposal; no Worker execution occurred.
- Generic cause: unnecessary setup elaboration can consume the response budget.
  Ask for one concise proposal, adding alternatives only for actual unresolved
  scientific ambiguity. This cannot guarantee control over hidden reasoning or
  provider truncation; preserve any further truncation as failure evidence.
- Change: rails/RL-0001.yaml, scoped to Navigator/onboard/all problem types;
  rails-0.2. Commit: recorded after local commit in the review package.
- Genericity: no table, filename, column, observed value, model or domain in
  instruction or reason. Valid for any study setup; no safeguard is changed.
- Offline verification: genericity and actual inference-request injection tests.
  Fresh live verification pending; do not relabel Round 1 as successful.
