# Project accounting (P16)

Implemented on `native-onboarding`; no live acceptance run has been performed.

## Commands

```bash
mlca --project /path/to/study usage
mlca --project /path/to/study usage --json
mlca --project /path/to/study usage --csv /path/to/usage.csv
mlca --project /path/to/study usage backfill
```

Usage covers the whole project, including retries and branches. CSV rows contain the project ID
and request metadata, never the request/response payloads. Nested metadata is JSON in a CSV cell;
unavailable scalar values are empty cells. `metrics` remains branch-specific.

## Fields and totals

Request records optionally retain the generation ID, reported model/provider, input/output tokens,
reasoning tokens, cache-read/cache-write tokens, upstream cost and charged cost. Reasoning tokens
are part of output tokens; cache counts are input-token details. Do not add these subsets to the
input/output totals. Upstream cost is separate from the charge to the OpenRouter account.

Every summary field has an `unknown_<field>_requests` count. Its value is the known subtotal, or
null when no value is known; `partial` identifies incomplete groups. An empty group has a zero
sum because there were no requests. For partial totals, evaluation metrics additionally expose `known_value`,
`unknown_requests` and `partial`, while their complete `value` remains null. Fully known totals
keep their existing value/source shape.
MCP tool envelopes do not count as model inference; external agent usage remains unavailable
until imported. Nothing estimates missing reasoning or caching measurements.

## OpenRouter settings

Structured output defaults to automatic: use JSON schema when the cached model catalogue reports
support. Explicit true/false configuration wins. A schema request requires compatible routing via
`provider.require_parameters`. Models > Advanced provides data-collection and zero-retention
routing preferences. These constrain routing; they do not establish confidentiality independently
of the provider policy or MLCA's documented trust boundary.

Each project sends a stable pseudonymous `user` hash, containing no filename, path or identity.
Standalone connection diagnostics have a separate pseudonym derived from their diagnostic session.
The exact settings are recorded. MLCA sends no model fallback list and does not change provider
fallback policy. Selecting `openrouter/free` explicitly still allows router-selected models; use
fixed model IDs for pinned-model comparisons and record the model/provider that actually answered.

## Backfill

This command performs authenticated metadata GETs, not inference calls. It is explicit and is never
run by summaries, metrics or tests. It considers OpenRouter requests with unavailable charged cost,
keeps existing values, merges under the request-envelope lock and preserves egress. Successful cost
recovery uses `cost_source: generation_endpoint`; `backfill_fields` identifies recovered fields.
Requests without a generation ID are listed as unrecoverable. Records outside 30 days, missing
provider configuration and metadata failures are reported without copying credential/error text.
Requests start at most once per second. Upstream generation costs are retained only for BYOK;
undocumented cache-write measurements remain unavailable. A fully accounted ledger is unchanged.

`usage reconcile` is not implemented yet: the author's actual Activity CSV is required before its
parser is written. Expected location in the paper repository:
`ES/submission2/experiments/10_agent_metrics/openrouter_activity/YYYY-MM-DD_by_model.csv`.
No files in that repository are modified by this implementation.

## Scope and verification

Worker-generated scripts remain the measured code path. Navigator failure falls back to template
choices after its bounded repair; it does not replace Worker code or hide integrity errors.
Level A remains the default where available, with level B only by explicit opt-in.
The live smoke test, Activity reconciliation and the remaining P14/P15 work are pending.

Primary API references checked during implementation:
- [Usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting)
- [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [Generation metadata](https://openrouter.ai/docs/api/api-reference/generations/get-request-%26-usage-metadata-for-a-generation)
