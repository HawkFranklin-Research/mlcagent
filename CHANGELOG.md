# Changelog

## Unreleased — work order 05 (16 October 2026)

- Activate consolidated rails-0.3; retain exploratory rounds separately.
- Normalize metric aliases against one task registry and bound model calls.
- Approved setup value inventories and validated, recorded label spelling maps.
- Record fitted columns and retain grouping metadata for training folds.
- Share batch rate state, support explicit unlimited budgets and rails ablation.
- Development batches use external setup/leakage scoring, never manifest answers
  in the agent prompt. Full validation and live outcomes are recorded separately.

## Unreleased — work order 04 Part B (16 October 2026)

- Correct the setup response contract and bounded local validation/repair; retain
  known setup-failure usage in aggregate accounting without inventing unknowns.
- Candidate RL-0001 requests concise setup proposals and meaningful alternatives.
- Round 1: twelve setup failures preserved; no completed live workflow or freeze.

## Unreleased — work order 04 Part A (16 October 2026)

- Autonomous `mlca run`: schema-only study inference, fresh repeated projects,
  unchanged Session safeguards, and retained failures/setup request evidence.
- Shared decision windows with CLI/TUI Halt, human alternatives/scoped custom
  instructions, policy attribution and recorded expiry/override timings.
- Autonomy, rails and actual model-distribution metrics; setup requests count in
  project usage and missing values remain unavailable.
- New workflow templates, label-excluded registration and external evaluator
  artifacts are offline-tested; live development acceptance has not started.
- Part B was subsequently authorized and has started; see the newer entry. No release/version change.

## Unreleased — multi-dataset development validation (15 October 2026)

- Preserve the original Worker work order during repairs; clarify named Path inputs, file formats, complete-pipeline prediction and instrumented Cox fits.
- Accept complete standalone Python as well as fenced Python, retaining static checks, sandboxing and fit enforcement. Fit refusals explain that temporary models also require instrumentation.
- Support NumPy scalar JSON values while rejecting non-finite values and arbitrary objects. Missing input keys produce safe, repairable diagnostics.
- Use indexed fingerprint lookups with unchanged matching semantics; inspect pandas table JSON and records JSON, refusing unsupported shapes.
- Return fixed library-contract hints without sending captured values or raw traceback text. Permanent tests cover earlier and new paths.
- Six-table live driver attempts use AI-written code only. Failures and logged continuations are retained as development evidence, not frozen measurements or guaranteed completions.

## Unreleased — P17/P18 local implementation (14 October 2026)

- Sealed external cohorts with attributed, bounded exposure; ordered bio-bench custom instructions and retained unsuccessful outcomes.
- Outcome-dependent integrity review on frozen training rows; wide-feature question review avoids redundant state/table reads.
- Isolated OpenCode, Claude Code and Codex brain-mode benchmark clients, numeric usage capture and summaries across arms.
- Curated evidence exports with private/data/environment exclusions; experiment preparation and draft cards live in the experiments repository.
- Full offline regression suite: 296 passed, 1 skipped. Reference biomedical acceptance and limitations are recorded separately; no live calls, measurement freeze or release in this work order.

## 0.2.0b2 (beta) — 13 October 2026

- Guided numbered action and human-decision cards, visible progress, a branch journey and literal readable logs.
- Provider switching between steps, recorded model changes, benchmark model locking and explicit connection/quota checks.
- Registered ChatGPT plan sign-in using MLCA's own configured client ID and public API; disabled until registration. No Codex identity is borrowed.
- Secure OS-keyring credentials, atomic study initialization and explicit archival of incomplete setups.
- Offline guided-user pilot, OAuth/refresh/stream checks, model-switch, quota and initialization regression tests; updated native and VM guides.
- Beta 2 publication and beta 1 yank are authorized; validation and actual publication results are recorded in docs/IMPLEMENTATION_STATUS.md.


## Unreleased — native onboarding (12 October 2026)

- File/folder picker, supported-table discovery, explicit main table and optional supporting inputs; split and replay select that table.
- Deferred outcome columns and plain-language study details, attributed resolution records, deterministic Onboard gate and original-answer preservation.
- Larger role-aware OpenRouter/OpenAI/local settings with session-only masked keys, budgets, searchable cached model catalogues and zero-price filter.
- No live provider calls, scientific runs or publication; native changes are isolated on native-onboarding.

## 0.2.0b1 (beta, prepared; publication blocked) — 7 October 2026

- Release gates pass (106 tests, 1 skipped). PyPI refused the initial upload because `mlca` is too similar to another project; no release is published.

- Author-approved package name `mlca` and CC-BY-NC-ND-4.0 licence; official legal code, SPDX metadata and npm licence mirror.
- First PyPI beta preparation: prerelease-aware release guards, pinned beta installers, and npm SemVer mapped to the exact Python prerelease pin. npm remains unpublished.
- Add the M7 VM brain-mode walkthrough and correct its portable data path and sandbox/trust-boundary guidance.
- Core and MCP functionality includes the R-MCP1b simple-copy guard; native-client, original-data and live-model validation remain pending.

## R-MCP1b: simple-copy detection — 7 October 2026

- Match table values regardless of column names at six and four significant digits; require
  min(3, column count) distinct cell matches in one source row alongside existing exact checks.
  Full-row fact checks also ignore names/order. Version-1 indexes upgrade atomically from
  unchanged registered sources without test decryption.
- Add regressions for renamed/rounded copies, readable describe/class/metric summaries,
  distinct-cell matching and migration. Clarify heuristic privacy limits and local driver use.
- Checked: 101 passed, 1 skipped; Ruff, wheel resources and installed-wheel 14-tool discovery pass.

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

## P10.1 — 7 October 2026

Lazy per-session RunSnapshot records capture hardware/software, role settings, template/environment hashes and sandbox capability without credentials. Provider-returned model IDs and actual request settings are in usage records. Unknown hardware remains null with unavailable source; sandbox capability is not execution verification. Snapshot/provider canary test: 1 passed; Ruff passes.

## P10.2 — 7 October 2026

Decision records now carry proposal/approval waits, instruction size and caller attribution; CLI/MCP active time stays unavailable. The TUI estimates activity from keyboard/mouse intervals and excludes complete gaps over 120 seconds. Script view edits record derived changed-line counts when a frozen reference exists. Timing/TUI tests: 6 passed; Ruff passes.

## P10.3 — 7 October 2026

A validated failure taxonomy is assigned at record/error boundaries for scope, gates, static/fit checks, runtime exception types, sandbox, timeout, missing outputs, providers, budgets, privacy and abandonment. AttemptFailed preserves failures repaired before terminal completion; typed FitRuleError identifies runtime fit refusals. Historical records remain uncategorized rather than retrospectively inferred. Taxonomy/engine/scientific/invariant subset: 25 passed; prior evaluation/store subset: 25 passed. Ruff passes.

## P10.4 — 7 October 2026

Offline mlca metrics writes sourced run, steps/recovery, failures, principal-separated interventions, time, model usage, egress, provenance, primary results, safeguards and decision sequences. Brain-mode external inference remains unavailable until import. Missing provider usage/cost now remains null; cost estimates are labelled derived. Root failures are counted separately from terminal wrappers. Driver golden/brain/repair/unknown-provider and invariant tests: 10 passed. Overhead retains approximate negative residuals when waits overlap.

## P10.5 — 7 October 2026

mlca usage import supports Claude assistant-message usage and Codex token_count deltas, project-window intersection, idempotent envelopes and growing Claude messages. Only whitelisted identifiers/model/timestamps/numeric fields persist; message content and transcript paths are excluded. Codex 0.160.1 field names were checked locally without displaying message content. Window/idempotence/content-canary/Codex-delta/CLI compatibility tests: 4 passed. Missing usage/cost remains unavailable.

## P10.6 — 7 October 2026

Headless task-card driver benchmarks create independent projects, invoke fresh providers, preserve failed runs, enforce per-run/total conservative request budgets and log user:policy/<card hash> approvals/choices. All split seeds stay fixed; seeded option policies vary by run. Summaries cover completion, failures, recovery, interventions, time, tokens/cost, final metrics and action/parameter agreement with unavailable sample counts. Three-run success and forced-failure (2/3 completion) tests: 2 passed in 129.65 s. Brain benches are refused; no live calls or original data were used.

## P10.7 — 7 October 2026

Documented sourced measurements, client-usage import, task cards and measurement limits in docs/metrics.md; added a task-card example and VM evidence commands. Strengthened failure-origin tests, metadata redaction and completed brain-mode metrics coverage. Targeted validation: 28 tests passed, plus the complete stdio brain-mode study test passed; Ruff passes. Full release-suite validation follows with the approved distribution name.

## 0.2.0b1 — evaluation instrumentation and distribution identity

Implemented P10.1–P10.7; approved distribution name is `mlcagent`, with unchanged `mlca` CLI/import/MCP names. Benchmark sequence agreement excludes unavailable metrics and reports the missing-run count. Release validation and publication results are recorded in docs/IMPLEMENTATION_STATUS.md.

## 2026-10-07 — P10 and mlcagent beta release gates

P10.1–P10.7 are implemented. Final full offline suite: **137 passed, 1 skipped in 603.43 s** (PowerShell unavailable); supporting-action/failure targeted subset: 20 passed. Ruff lint/format, approved-name/version guard, wrapper synchronization, build/Twine and 186-entry wheel resource checks pass. The final isolated HOME/XDG wheel walkthrough passes install/version/doctor, synthetic init, Claude project/skill permission preview without writes, bubblewrap namespace probe and stdio discovery of all 14 tools. No live models, original anemia data or native client/OS validation were performed. The authorized PyPI upload as `mlcagent` 0.2.0b1 follows; npm/GitHub operations remain unauthorized.

## 2026-10-07 — mlcagent beta published

Published wheel and sdist for [mlcagent 0.2.0b1](https://pypi.org/project/mlcagent/0.2.0b1/) from local source `16bcc72`. PyPI accepted the token and both artifact hashes match. No GitHub push, npm publication or new remote occurred. Fresh-index install/version/doctor/14-tool verification passed. The frozen beta README retains an overlooked historical Status paragraph about the rejected mlca name and the old test count; source README Status is now corrected for the next release. No artifacts are replaced or additional releases uploaded. Project-scoped token replacement and removal of the account-wide token file remain an author account step; the credential is not reopened.

## 2026-10-07 — Published-beta verification

[PyPI release](https://pypi.org/project/mlcagent/0.2.0b1/). Fresh PyPI verification used an empty temporary HOME/XDG and uv cache: `uv tool install mlcagent==0.2.0b1`, `mlca --version` (0.2.0b1), `mlca doctor --json` (level A capability; execution must confirm isolation), and `mlca mcp doctor` (14 tools) all passed. Published wheel/sdist SHA256 hashes match the scanned release artifacts. Local tag `v0.2.0b1` points to release source `16bcc72`; no push. P10 is complete, while M7, real providers/data, and native macOS/Windows remain pending. The beta description contains an overlooked historical README Status paragraph; it is corrected in source for the next release, with no second upload. Token rotation to a project-scoped token and removal of the account-wide file remain an author account step; the file was read only by the publish command.

### Native OpenRouter sign-in (unreleased)

- Start free with OpenRouter in model settings: PKCE browser authorization or masked headless code.
- Secure OS keyring storage; session-only TUI fallback with no plaintext persistence.
- `mlca signin`, `mlca signin --headless`, `mlca signout`; doctor reports local credential availability.
- Navigator/Worker free-router preset, preserving other role and generation settings.
- Offline PKCE, callback, secret storage, redaction, configuration and TUI regressions.

### Existing project folders (unreleased)

- Creating a study in an existing project folder now offers resume, fresh subfolder or cancel.
- Preserve earlier attempts and new-study form; clarify backend overwrite refusal.

## P11.7 — Guided-user regression and release preparation

Final focused native/auth/model/initialization coverage: 45 passed in 14.57 s; the later queued-switch/pilot/status subset passed 5 tests in 4.67 s. The beta-wrapper pin test also passes in isolation. The full offline suite is still pending at preparation time. No live model calls or OAuth authorization were made.

Beta 2 validation caught and corrected a failed-init empty-folder residue. Cleanup removes only
the new empty study root; existing/user-added content is preserved. Initial full run: 190 passed,
2 failed, 1 skipped; corrected initialization and wording regressions: 6 passed. Final rerun pending.

## 0.2.0b2 final validation — 13 October 2026

Full offline suite: **193 passed, 1 skipped in 647.09 s** (PowerShell unavailable). Ruff lint/format, release metadata and wrapper checks pass. Rebuilt wheel/sdist pass Twine and the 206-entry wheel check. Isolated HOME/XDG install, version/doctor, synthetic initialization and 14-tool MCP discovery pass; Claude registration/skill preview writes no configuration. No live models, real OAuth authorization or original-data study was run.

## Beta 2 published and beta 1 yanked — 2026-10-13

Published [mlcagent 0.2.0b2](https://pypi.org/project/mlcagent/0.2.0b2/) using the authorized upload token; both public artifact hashes match. Fresh isolated HOME/XDG PyPI install, version, doctor and 14-tool MCP verification pass. Beta 1 is yanked (both files), verified in release management and public PyPI JSON. Local tag v0.2.0b2 records release source bdc2f376ef2b9b2848d5f5ed5b272ee9aad2a311; global mlca was refreshed to 0.2.0b2. No GitHub/npm push or publication occurred. Master and uncommitted browser plans remain untouched.

Final suite: 193 passed, 1 skipped in 647.09 s; lint/format, metadata, wrappers, Twine, wheel resources and isolated synthetic init/permission-preview pass. Real OAuth/model/data validation and OpenAI registration remain pending. The token was read only by the publish command and never displayed, copied or committed.

## MX1 — MCP human card contract

Guided MCP cards expose actor/how, preserve colon-containing IDs and refuse human choices with a logged human_decision and request route. Deferred onboarding emits an engine-only empty menu without model calls. Focused card, guidance and click-only pilot tests pass.

## MX2 — Proposed study fields and human resolution

Added validated study_fields requests without applying suggestions, human CLI approval with JSON editor, and prefilled TUI Study details. Resolution records proposer and decider separately. Deferred MCP init reports the next request route. Eight focused proposal/decline/invalid-column/CLI/edit/guard/init regressions pass (10.52 s).

## MX3 — Live TUI observer

Added transient MCP client presence and one-second incremental log polling. Observer cards refresh without invoking models; agent work greys nonhuman cards while human approvals remain accessible. Brain mode identifies its driver instead of requesting provider setup. Confirmation approvals may resolve while a script is awaited; running mutations wait briefly on the existing lock. Study-field changes still require an idle step because they invalidate its work order. Textual second-session/thread and waiting-script approval tests pass (four focused tests, 9.84 s). Presence files are presentation hints, never authorization or immutable evidence.

## MX4 — Bounded journey and phase projections

Added actor-labelled last-12 action trails, last-10 plain messages and canonical per-step phases. StepProgress persists controlled metadata for cross-process readers; terminal status is authoritative. Progress notifications use only a current request and unsent phase history on polling. One response envelope per call remains; prepared progress metadata is hashed/countable separately and delivery is explicitly client-dependent. Failure messages expose safe categories rather than raw errors. Phase order, privacy, callback and TUI regressions pass offline.

## MX5 — Guided agent instructions and VM workflow

Server instructions remain 15 lines, explain actor/how and deferred study-field requests, and default to numbered user choices unless autonomy was requested. The packaged skill and VM guide cover live TUI watching, approvals, deferred targets and request-scoped notifications. The guide distinguishes unpublished MX source from public beta 2. Seven focused instruction/protocol/card/proposal/live-TUI tests pass (10.99 s). No live model or browser calls.

## MX6 — Attribution and brain-mode metrics

Approval requests, study proposals/deciders and human_decision refusals are counted by actual principal. Metrics expose agent-requested approvals, measured resolved human waits, pending requests and the agent script share (all started steps denominator; unknown sources remain unavailable). Run mode now follows step execution rather than the last human-approval snapshot. Six focused synthetic attribution/approval/phase/live-TUI tests pass (16.50 s). MX5 installed source refresh and 14-tool probe passed; no new beta published. Full offline suite follows.

## MX final acceptance

MX1–MX6 implemented in ordered local commits. Full offline suite: **202 passed, 1 skipped in 719.16 s** (PowerShell unavailable). Ruff lint/format pass. Installed source refreshed after MX5; final refresh includes MX6. No live model calls, computer controls, remote pushes or beta 3 publication. Public beta 2 is unchanged; local development source still reports 0.2.0b2. Master and browser plans remain untouched.

## MX review follow-up — 13 October 2026

Study-field updates display an Onboard re-check rather than a misleading continuation. Approval resolution records include their kind and display “You approved: study fields” (or declined); old records without a kind remain readable. Invalid study-field proposals use `invalid_request`, while integrity exceptions are preserved. Offline regression coverage includes invalid columns, unknown fields, non-text fields, malformed proposals and the presentation messages.

The initial destination selection was superseded by the author: use HawkFranklin-Research, not VatsalPatel18. The newly created personal repository was empty and was deleted with the supplied credential (never displayed or persisted). Its local remote was removed. No code was pushed. The organization destination is awaiting identification; publication is paused for that discussion. The frozen master and untracked browser plans remain untouched. No package version change or PyPI upload is authorized by this follow-up.

## P16 — Project accounting and routing (13 October 2026)

Implemented optional generation/provider IDs, reasoning/cache-write tokens and upstream costs;
project/model/provider summaries with known subtotals, unknown counts and partial flags; usage CSV
with project IDs; pseudonymous OpenRouter user IDs; cached-catalogue automatic structured output,
compatible routing and advanced privacy preferences. Backfill fills only unavailable fields, retains
egress, spaces metadata requests at one second and lists unrecoverable/skipped/failed requests.
No live calls occurred. Activity reconciliation remains blocked on the author's actual CSV.
Focused offline subsets pass; the full suite follows. Worker execution and A/B opt-in rules are unchanged.
The implementation also preserves accounting for provider refusals, displays unknown cost safely in
the TUI and retains older evaluation value/source shapes for fully known values.

Existing uncommitted P13/catalogue/browser work is preserved. P16 needs only the existing catalogue
JSON-support property; that small dependency is included separately from the catalogue-snapshot work.
No publish, push, tag, version bump or installed-tool refresh is performed.

## P14.6 — Navigator recovery within the revision cut

Navigator JSON gets at most one repair. Provider errors, exhausted suggestion budgets and unexpected
response failures leave template choices available and log a safe plain-language fallback reason.
Integrity errors still stop. Worker steps, repair limits, failure records, fit rules and test unlock
remain unchanged; no reference script substitutes for a measured Worker failure. Six focused
Navigator regressions pass, including repair/caching and integrity-stop behavior. Combined isolated
P16/P14.6 candidate checks: 34 passed. Final full-suite verification follows.

## P16/P14.6 final offline acceptance

Full offline working-tree suite: **245 passed, 1 skipped in 678.51 s** (PowerShell unavailable). Ruff lint and formatting pass. The isolated selective P16/P14.6 candidate passed 34 tests, independently of the other uncommitted work.
An earlier run identified a legacy external-usage shape mismatch; complete totals now preserve the value/source contract. The corrected suite passed. Activity reconciliation and live smoke remain pending; post-freeze P14/P15 work is deferred. Existing uncommitted work is preserved.

## P14.4 — Generic pre-split data review

Added property-based findings, bounded questions, explicit sensitive decisions, replayable DataDecision/TaskConfigured records and immutable prepared inputs. Raw inputs are never modified. Approved excluded columns leave the prepared feature table; grouping columns are used for assignment and removed from model partitions. Review decisions cannot be changed after freezing, and pending questions block actions/transitions. Detection is heuristic (aliases, low-cardinality mappings, separating ranges and name hints), not proof of all leakage. Existing manual API projects retain compatibility; the P15 turn entry enables review. Initial baseline: 248 passed, 1 skipped. Data-review/gate/scope subset passes offline. No live calls or original-data scientific study.

### Unreleased: guided study turns

- Add recorded questions, docked answers, guided choices, explicit sensitive decisions and resumable autopilot.
- Keep model comparisons explicit, human approvals engine-owned, and result summaries tied to recorded outputs.
- Add two MCP question tools; legacy project snapshots remain unchanged.

### Unreleased P17

- Sealed external-cohort roles and single frozen-variant exposure at execution time.
- Ordered `mlca bio-bench run` instructions with verbatim outcome exports.

### Unreleased P18 integrity

- Outcome-dependent review uses frozen training rows only; strong numerical predictors default
  to keep-and-flag with explicit review.
- CLI validation and engine errors show their actual redacted messages.

### Unreleased P18 brain benchmarking

- Isolated OpenCode, Claude Code and Codex headless runners over MCP.
- Separate policy approvals, client-reported usage and cross-arm summaries.

### Unreleased P18 exports

- Curated, checksum-verified bench/bio-bench exports excluding private inputs and environments.
- Verbatim custom outcomes retain refusals and incomplete protocol status.

## Work order 04 A1 (unreleased)

- Add validated, scoped and snapshotted workflow rails with an immutable run hash.
- Keep historical projects and safeguards unchanged; baseline rails-0.0 has no new rules.
- Exclude dataset inputs from source distributions as well as wheels.

## Work order 04 A2 (unreleased)

- Add regression, multi-output classification, clustering and representation templates.
- Remove configured evaluation labels before registration and inventory.
- Add checked local per-row output artifacts and pre-split entity aggregation actions.
- Generalize outcome readiness and expose group/time split policies without relaxing test or fitting rules.
