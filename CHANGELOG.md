# Changelog

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
