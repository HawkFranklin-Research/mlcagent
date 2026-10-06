# Implementation status — 7 October 2026

## Current result

MCP M0–M6 is complete: **81 passed, 1 skipped** in 360.22 s, plus final focused
registration/init/guard checks (7 passed), Ruff lint/format and installed-wheel tool discovery.
M7 is the manual author checklist in [MCP docking](mcp.md). No live models or original data
have been used. Earlier validation entries below are historical phase results.

## Prompt 01 validation

Command: `uv run pytest -q` (offline tests set `UV_OFFLINE=1`, including slow tests).
Result: **40 passed in 263.43s (0:04:23)**.
`uvx ruff check src scripts tests`, `uvx ruff format --check` and `git diff --check` also pass;
Ruff's cache was explicitly directed outside the repository.

| Phase | Source implementation | Execution validation |
|---|---|---|
| P0 | Package/environment bootstrap | CLI help/version and real analysis environment creation checked |
| P1 | Event schemas, hash chain, replay, branches | Incremental/full verification, tamper messages, branch recovery, lazy sessions and 5,000 appends checked |
| P2 | Templates, checks and gates | Both template structures, any-of output checks and primary/supporting roles checked; classification gates exercised end to end |
| P3 | Project lifecycle | Inventory, structured column resolution, interactive/non-interactive init and legacy column fallback checked |
| P4 | Execution and test lock | Level A private-path/network probe; level A/B workflows, test lock, cleanup and exact fit-index refusals checked |
| P5 | Providers and request evidence | Offline fake provider, usage/egress correspondence checked; real providers remain untested |
| P6 | Roles, turn loop, Session API and CLI | Full synthetic classification path and fresh-environment standalone-script replay pass at levels A and B |
| P7 | Textual interface and reports | Welcome banner/footer, project opening, quit, readable logs and deterministic reports checked |
| P8 | Survival and hardening | Survival init/columns/template structure and post-exposure fitting refusal checked; full survival workflow remains untested |
| P9 | Later UI/account capabilities | Not implemented; Prompt 02 authorizes distribution preparation separately |

## Regression sensitivity

The required local reverts failed as expected and were restored before the passing run:

- F3: reverting checks.py caused `test_output_exists_any_of[True]` to fail with `KeyError: 'action'`.
- F6: reverting store.py caused `test_incremental_read_and_hash_chain` to fail with
  `Failed: Unexpected full log reread`.

The 5,000-append benchmark initially completed in 1.556 seconds; the permanent test enforces a 30-second
bound on this host. Tests use reviewer-derived synthetic fixtures and no API keys or original data.
Dependency priming happens before offline runs; see [testing](testing.md). A first run exceeded the
small `/tmp` quota, so test scratch lives outside the repository on the cache filesystem and projects
are cleaned after each test. That failed attempt is not counted as passing validation.

## Limits and author decisions

Original anemia data will be supplied later. These runs establish harness behavior, not scientific
case-study results. Full survival, live providers, broad UI navigation, adversarial/native-code
coverage and cross-platform execution still need validation. Template content remains DRAFT.
Licence, public package/repository names and default models remain author decisions. No remote,
tag, push, release or publication has been created.


## Prompt 02 distribution validation

Final command: `uv run pytest -q` (offline, slow tests included).
Final result: **54 passed, 1 skipped in 227.66s (0:03:47)**. The skip is PowerShell syntax/analyzer
validation: neither pwsh nor PSScriptAnalyzer is installed on this Linux host.

Prepared: dynamic Python metadata, wheel/sdist with templates/styles/derived artwork/runtime helper,
loopback-only browser TUI, portable scrubbed processes and audit paths, shell/PowerShell installers,
version-pinned npm launcher, generated Homebrew formula, cross-platform CI and gated release workflows.

Additional checks:

- Ruff lint and full format check; Git whitespace check: pass.
- `uv build` / check_wheel.py; fresh clean-home `uv tool install` and version/doctor JSON/banner: pass.
- Missing web-extra refusal and real loopback HTTP start/stop: pass.
- `node --test packaging/npm/test/`: four tests pass (arguments/pinning/debug, status, missing uv, signals).
- Shell installer fake-uv install/upgrade/pin/PATH dry runs and `sh -n`: pass.
- `npm pack --dry-run`: exactly package.json, bin/mlca.js, README.md and LICENSE.
- Homebrew dummy-hash rendering and `ruby -c`: pass. Final preview uses the local sdist hash.
- Workflow YAML syntax and licence/name/tag/sequence guard tests: pass.
- 5,000 append test under concurrent suite load: 7.576 seconds, below the 30-second bound.

Unavailable here: shellcheck, pwsh/PSScriptAnalyzer, actionlint, act and Homebrew execution; the tools
are absent. Native macOS/Windows and Python 3.11 execution were not run on this Linux/Python 3.13
host; the six-job CI matrix is prepared but not triggered. Level B is exercised locally, not presented
as native-OS validation. Full survival/original-data scientific studies and live providers remain untested.

D1 licence and D3 public name remain publication blockers. The protected GitHub environment and
registry/tap setup must be configured by the author as described in [releasing](releasing.md).
No remote, tag, push, workflow trigger, release, registration or publication was performed.

## 2026-10-07 — MCP M0

Core prerequisite regressions added: gate refusal, untrusted model completion claims, Navigator repair/fallback, zero-call deterministic scope rejection, immutable step modes, invalid fact rejection, Worker static-failure repair, budget refusal, rate-limit retry and a credential canary scan. Targeted offline run: 7 passed. Live providers remain deferred. Incoming author/reviewer edits were preserved in a separate local checkpoint.

## 2026-10-07 — MCP M1

Caller principals are persisted for decisions and branch operations. Human-only confirmations, test unlocks and package approvals refuse agents in Session. Approval requests can be resolved through CLI/TUI; unlock still requires the exact phrase, and stale event/branch requests refuse approval. Brain steps persist ScriptRequested work orders and resume after reopen; both sources share run_attempt. Test decryption now lasts only around each execution. Active steps block movement/branching and package approval. Model calls are disabled at Client in brain mode. Background operations hold the same action lock; polling is available through step_status. Reports split decisions and script attempts by principal/source.

Validation: full offline suite 63 passed, 1 skipped (PowerShell unavailable), 242.09 s; focused engine/scientific checks after final guard edits: 4 passed. Unit/TUI subset: 28 passed. No live models called.

Deviation: an operation that has not reached StepStarted within one second returns a temporary operation ID; step_status resolves it to its eventual persisted step ID. This keeps provider option generation from blocking MCP. Operation IDs are connection-local; actual steps/work orders are persisted. Plain CLI/TUI remain blocking driver clients.

## 2026-10-07 — MCP M2

Official SDK mcp 2.3.0 is a core dependency (`mcp>=2.3,<3`); it exposes MCPServer, the successor of FastMCP. The real stdio doctor negotiated MCP 2026-07-28. In-process tests cover both modern auto negotiation and the legacy initialization path. Seven initial read/setup tools, compact views, indexed evidence reads, Context-derived agent identity, server instructions and `mlca mcp`/doctor are implemented. Protocol/read tests: 2 passed. CLI startup errors now use stderr so they cannot corrupt the protocol stream.

Resource deviation: the SDK disallows Context injection in static resources. Views therefore use `mlca://view/{kind}` (status/facts), ensuring per-request attribution and accounting. Optional tasks remain deferred because polling is universal and the SDK does not implement that extension. SDK references: https://github.com/modelcontextprotocol/python-sdk/releases and https://py.sdk.modelcontextprotocol.io/ .

## 2026-10-07 — MCP M3

Driver-mode choices/custom work run in background threads, movement/branches use Session, and human requests route to CLI approvals. MCP option IDs include the OptionsProposed record ID, rejecting consumed or stale menus. Polling reports running until execution, checks, facts and views finish and the project lock is released. Completed events refuse direct custom actions as well as offering only transitions.

Validation: MCP protocol plus full synthetic driver path and concurrent locking in both directions: 4 passed (30.70 s). Agent approvals were resolved by the human CLI; attribution/integrity checked. Persisted external-step regression: 2 passed. No real providers called.

## 2026-10-07 — MCP M4

All 14 stable tools are registered. Brain mode validates submitted options and scripts through the shared engine and returns persisted work orders/repair diagnostics. Option IDs are evidence-bound. Work-order hashes are computed after credential redaction. Runtime fact candidates with missing outputs now explicitly produce FactRejected instead of being silently dropped.

Validation: brain full synthetic classification path (including human approvals, image read and fresh-script replay) completes with Client.complete disabled and roles/providers removed. Brain bypass/attempt-limit tests and submitted execution guard tests at both available isolation levels: 4 passed, 87.42 s. Guards exercise forbidden imports/direct fit, validation fit, outside writes, and dynamically constructed paths to the real vault/key/original data. Protocol and persisted engine subset: 4 passed. No real models called. Background submission validates the persisted step state rather than its transient polling status.

## 2026-10-07 — MCP M5

Each dispatched tool/resource result creates one recoverable usage/egress envelope: principal, tool, duration, application-body bytes/hash and content categories. No result content is stored in that ledger. Calls before a project opens use an external per-server user-data ledger. Protocol/schema rejections outside a dispatched tool are handled by the SDK and are not project operations. SDK-added transport identity metadata is outside the application digest.

MCP usage has cost_source external: external agent tokens/cost are unavailable, not a claim that its inference is free. Model requests and external tool calls are counted separately, and tool time is excluded from LLM latency. Read views suppress raw inventory rows and stdout/stderr, and allow only indexed/hash-checked scripts, PNG figures, reports and bounded summary tables. Untrusted content stays under data fields and summaries are fixed text. Figure reads return ImageContent; evidence resources use query refs. Unknown exceptions expose their type only; application refusals are logged when the action lock is free, otherwise in the request ledger.

Validation: complete MCP suite 10 passed (122.70 s); focused ledger/privacy tests 2 passed after final changes. Tests verify one envelope per dispatched call, exact body hash/bytes, no synthetic-row canaries or fake key in results/ledgers, and external calls not counted as unknown model costs. These checks cannot prove arbitrary generated artifacts never encode individual data; summary content/figures still require scientific inspection. Same-user filesystem/CLI access is not authenticated by MCP clientInfo; human-only enforcement is an API boundary, not an OS identity guarantee.

## 2026-10-07 — MCP M6

Client registration previews/helpers, a bundled 38-line agent skill, MCP setup/tool/approval docs,
and updated README/plans are implemented. Helpers require --yes, back up existing files, run
CLI argv without a shell and preserve Cursor settings. Registration flags were checked for
installed Claude Code 2.1.291, Codex 0.160.1 and Hermes v0.21.5+8071; absent OpenClaw/Cursor
use official formats with native validation explicitly pending. MCP checkout now returns only
its compact overview, briefs scrub known credential values before persistence, unexpected
submitted-step failures freeze evidence, and bounded Parquet reads inspect row metadata first.

Guard sensitivity: disabling the human-principal check made
`test_agent_refusals_and_human_approvals` fail (1 failed, 0.74 s); disabling deterministic
scope rejection made `test_mcp_layer_one_rejects_before_step` fail (1 failed, 1.27 s).
Both guards were restored byte-for-byte before the final suite. Focused helper/init/guard tests
passed (7 passed, 2.37 s); bounded CSV/Parquet and init checks passed (2 passed, 3.45 s).
Skill validation, Ruff lint/format, wheel resource validation and a clean installed-wheel stdio
doctor pass. The doctor negotiated 2026-07-28 and found all 14 tools. Native client registration
was not performed; the wheel doctor used a client-free PATH and isolated MLCA config/data.

M7 remains an author-run checklist in docs/mcp.md: Claude/Codex/Hermes brain and live-provider
TUI driver. Anemia data, native macOS/Windows and live provider validation remain pending.

Final M6 validation: `uv run pytest -q` — **81 passed, 1 skipped in 360.22 s**.
The skip is PowerShell validation because pwsh/PSScriptAnalyzer are absent. The focused
helper/init/guard subset was rerun after the final Claude config-target correction (7 passed).
Ruff check and format check pass (140 files); Git whitespace check passes. Both templates
remain the author's incoming concise v0.2.0 content. No model calls, original-data runs,
client registrations, remote operations or publication were performed.
