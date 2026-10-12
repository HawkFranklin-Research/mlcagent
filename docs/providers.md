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

## OpenRouter sign-in (native driver mode)

In **Models and providers**, choose **Start free with OpenRouter**. Authorize your own
OpenRouter account in the browser, return to MLCA and save settings. Navigator and Worker
are selected as `openrouter/free`; other roles and generation settings are preserved.
No MLCA gateway, app registration or client secret is required. Requests go directly to
OpenRouter, whose selected downstream model receives the request under your privacy settings.

MLCA uses PKCE S256, a random state, a loopback-only callback on a temporary port, a ten-minute
local expiry and a single exchange. Callback access logging is disabled. For SSH, use the
**SSH / paste code** button: OpenRouter displays an authorization code, entered in a masked
field. It is not a model API key. The authorization URL is shown for copying.

Only supported secure OS keyrings (Linux Secret Service, macOS Keychain, Windows Credential
Locker) can remember the returned user-owned key. There is no plaintext/file fallback.
If unavailable, the TUI offers session-only sign-in: reconnect after restarting MLCA.
Pasted API keys retain their existing session-only behavior. Config contains only a credential
reference, and keys are registered with redaction before use. Analysis subprocesses do not
receive the key. An unlocked local keyring remains accessible to other processes running as
the same user; this does not create a new operating-system trust boundary.

CLI, with a working secure keyring:

```bash
mlca signin
mlca signin --headless
mlca doctor --json
mlca signout
```

`signin` explicitly changes the global Navigator/Worker selection to the free router. Project
configuration overrides still apply. `doctor` checks local credential availability, not account
identity, quota or inference connectivity. Sign-out removes the local stored key; revoke its
remote access separately at [OpenRouter key settings](https://openrouter.ai/settings/keys).
Already running MLCA processes must restart after another process signs out.

### Free requests and measurements

Free is not unlimited. OpenRouter currently documents 20 requests/minute and typically
50 free requests/day without purchased credits, rising to 1,000/day after at least $10 in
credit purchases. Failed requests can count. Availability and limits can change; see
[limits guidance](https://openrouter.ai/blog/tutorials/how-to-get-the-lowest-cost-llm-inference-on-openrouter/).
A full study is not guaranteed to fit within the quota. The existing bounded retry behavior
still applies; do not repeatedly retry an exhausted daily quota. No paid fallback is added.

The free router can select a different model for each request. MLCA's usage ledger records
both the configured ID and `model_reported`; use a fixed model for comparisons requiring fixed
model identity, or explicitly report a router policy. The free preset writes sourced zero-token
pricing for that router, rather than setting a zero request bound on arbitrary future models.
Navigator caching/call-frequency changes, streaming and fallback configuration are separate
work; this sign-in change does not alter the scientific workflow or remove scope checks.

Protocol source: [OpenRouter OAuth PKCE](https://openrouter.ai/docs/guides/overview/auth/oauth).
Localhost app attribution uses the host/port; MLCA does not promise a branded marketplace identity.
