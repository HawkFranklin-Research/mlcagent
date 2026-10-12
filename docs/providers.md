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

## ChatGPT plan sign-in (P11.5, registration-gated)

**Continue with ChatGPT** is disabled until `chatgpt_auth.client_id` holds MLCA's own issued
`oaiapp_…` registration. No Codex CLI client ID or private ChatGPT backend is used. The official
OSS flow can issue a per-user/workspace client during registration; this implementation deliberately
waits for the author-selected registration rather than dynamically registering it for you.
[Registration and sign-in](https://developers.openai.com/siwc/token-sharing-open-source/sign-in)
explains the account/host distinction and consent.

Set your issued ID in global config, then use Models or `mlca signin --provider openai`.
For SSH use `--headless`, authorize in the browser, and paste the complete redirected loopback URL
into the masked terminal field. The documented loopback PKCE flow is used; no undocumented device
endpoint is guessed. A stable UUID host ID is non-secret metadata. State, nonce, callback, JWT
signature/issuer/audience/expiry and granted plan-use scope are validated before activation.

Access/refresh/ID tokens are a single secure-keyring record per registered client. Refresh is
serialized across processes and rotates the record together. No plaintext fallback. Sign-out with
`mlca signout --provider openai` attempts revocation and removes local tokens, reporting if remote
revocation was not confirmed. [Accounts and sessions](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions)
describes those requirements and upstream plan limits.

Choose a model from your authenticated account catalogue; there is no hard-coded default. Inference
uses the public `https://api.openai.com/v1/responses`, `store=false`, `stream=true`, and accepts only
a `response.completed` terminal event. Incomplete/failed/interrupted responses are not executed.
See [Models and inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference).
Plan usage is not priced as API USD: MLCA records returned tokens and unknown monetary cost; plan
and permitted-credit caps belong to OpenAI account settings, not MLCA's USD budget. No paid-provider
fallback is configured. Identity sign-in alone never authorizes inference.

Offline mocks verify protocol behavior. Registration, eligible account access, native keyring behavior
and actual inference remain author-run checks; none was performed during implementation.


## Switching and status (P11)

Open Models with m at any time. Switching is applied at a step boundary, clears stale menus/clients,
and records ModelChanged with who changed which role and why. On reopening, recorded model/provider
settings take precedence over the initial project configuration. Reports and metrics retain changes
and actual returned model IDs. Bench --lock-models records a durable lock; it forbids configuration
switches, not changes chosen upstream by a router. Prefer a fixed model for fixed-model measurements.

The status dot uses observed success, 429/slow requests or failure. A configured credential is not
proof of a working connection. Test connection is explicit, one attempt per role, logged and budgeted;
it sends only a tiny instruction. Refresh quota is a separate explicit OpenRouter metadata request.
Only known nonnegative daily used/limit fields are shown, labelled as the last provider refresh and
bound to the credential's non-secret fingerprint. Missing fields remain unknown.

Optional Remember API keys stores pasted keys in supported secure OS keyrings; unchecked input
remains session-only. Never put a key in YAML. mlca auth status lists local availability/storage only,
not secret values. Earlier descriptions of pasted keys being exclusively session-only predate P11.
