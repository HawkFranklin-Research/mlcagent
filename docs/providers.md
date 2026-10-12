# Model providers

Copy `examples/config.yaml` to `~/.config/mlca/config.yaml` or use `mlca config edit`. Model identifiers
are supplied by the user. Navigator and Worker can use different providers/models. Inspector is optional.
No account/subscription login or third-party public gateway credentials are implemented.

Supported kinds: `openai_api`, `openrouter`, `openai_compatible`, `fake`. Credentials are environment
variables or author-approved masked TUI input retained only in the application process; YAML stores
variable names or non-secret session references, never pasted values. `openai_compatible` supports local servers with no API key.
Remote custom endpoints require HTTPS. Real requests require a known price in `pricing.yaml` or an
explicit `request_cost_bound_usd`; the bound is a user assertion used conservatively, not a provider
billing guarantee. Unknown actual costs remain unknown in the ledger.

`structured_outputs: true` enables JSON Schema response_format for compatible models. Otherwise the
client parses JSON text and validates with Pydantic, with one repair attempt. Unsupported models may
reject specific generation settings; omit temperature where necessary and select compatible models.
The OpenAI adapter uses the official SDK with SDK automatic retries disabled, so the wrapper records
every attempted call. [Official API reference](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create)
documents JSON Schema response formats and completion-token limits.

Provider 429/5xx retries are bounded and recorded individually, including unknown usage on errors.
Usage summaries distinguish known cost from unknown-cost requests. Request bounds are counted toward
budgets even when the provider omits billing data. Concurrent requests serialize budget reservations.
A configured bound can underestimate actual billing; verify prices before running expensive workloads.

The fake provider consumes YAML responses with optional `match` fields (role, purpose, event_id,
action_id) or call_index. Each response supplies text or a structured response and optional token counts.
No synthetic study is executed automatically. Use it for future offline validation once authorized.

## Native configuration screens

See [native onboarding](native-onboarding.md) for provider dropdowns, shared/separate role settings,
explicit catalogue refresh, search/free filtering and request/turn/session bounds. Catalogue prices
are cached with their source and timestamp; unknown/non-token fees need a request bound.
Pasted keys must be entered again after restart and are not available in another CLI process; use
environment variables for CLI/bench work. Forgetting pasted keys also drops the TUI's cached provider
clients. No connection or paid generation test is performed when saving configuration.
