# Changelog

## MCP review fixes R-MCP1/R-MCP2 — 7 October 2026

- Index private salted row fingerprints at registration and splitting; refuse copied table rows
  and full-row facts with sample rows disabled. Collection flags survive replay and reports;
  legacy reads are rechecked. MCP report reads omit run stdout/stderr.
- Claude setup previews recommend project denies for data, private state, keys, evidence copies
  and native shells; --yes backs up and merges settings. Other clients receive guidance.
- Reports describe external agent file access as unknown. Docs and bundled agent guide explain
  native-tool bypasses and derived-output disclosure limits.
- Author-approved supporting actions are now available before/after completion; next comes first
  when done, with unrun supporting actions and scoped custom. Primary alternatives still require
  a branch before their step. Supplementary steps preserve completed checks and generations.
- Checked: full offline suite 96 passed, 1 skipped (PowerShell unavailable), Ruff, skill validation,
  wheel resources and installed-wheel stdio discovery of all 14 tools. No actual client registration.

## Template content v0.2.0, output contract, MCP plan — 6 October 2026
- Both workflow templates now have short, specific content: one-sentence goals, state-phrased sub-goals,
  one-sentence custom scopes, and three-line Do/Save/Record action prompts with concrete defaults.
  Ids, outputs, roles, builtins and check types are unchanged; `max_options` is 3.
- New sub-goals: primary metric recorded on validation and on test (`metric_present`; `roc_auc` for
  classification, `c_index` for survival).
- Worker prompt: output contract (required outputs plus at most one figure, summary tables at most
  50x12, at most 5 printed lines, numbers via record_metric or cited facts; allowed fact keys passed in).
  Navigator prompts: shorter titles, reasons and fact values.
- `docs/templates.md`: "Writing content" rules. README rewritten. `plan_mcp.md` added (MCP docking,
  brain and driver modes). `plan.md` status updated.
- Checked: both templates validate; ruff passes; `uv run pytest -q` gives 54 passed, 1 skipped.

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
- B: portable scrubbed subprocess paths, private temporary homes, Windows-normalized audit roots and
  explicit per-OS doctor guidance. Weaker execution remains opt-in.
- C: cross-platform CI and a sequential, decision-gated release workflow with protected publication
  jobs, checksums, PyPI OIDC, npm provenance and an optional Homebrew PR. Workflows are files only.
- D: consent-based shell/PowerShell installers, a version-pinned npm launcher with no install hooks,
  generated wrapper identities and Homebrew formula rendering. Local fake-uv dry runs pass.
- E: install/release documentation, shared test helpers and explicit UTF-8 portability for resources,
  logs, scripts and streams. Final offline suite: 54 passed, 1 skipped (PowerShell unavailable).
- Local artifacts/installers are prepared; D1/D3 and author infrastructure setup still gate publication.

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
