# Implementation decisions

## 2026-10-07 — R-MCP1b

- Reviewer repros at 6103b55 renamed all columns or rounded to four decimals. The row guard now
  indexes numeric cells at six and four significant digits and matches values across all column
  names. A table heuristic requires min(3, returned column count) distinct returned cells to
  match distinct source cells in one source row. Bipartite matching prevents counting one common
  source value repeatedly. The original exact shared-column check is retained as an additional
  detection path; full-row facts keep the full-row requirement but ignore names and order.
- Index schema version 2 adds cell precision and an index for cross-column lookups. Version 1
  migrates atomically from unchanged registered sources, leaving the old file intact on failure.
  Registered rows already cover all historical split subsets, so old partition-specific profiles
  need not be reconstructed/decrypted during migration. Future splits store both precisions.
- Four significant digits is not equivalent to four decimal places for every value. The reported
  round(4) reproduction is tested; other scales, encoding and inference are outside the guarantee.
  Tables can be conservatively refused by coincidental matches in small/categorical datasets.
- Documentation and generated trust reports describe an accidental/simple-copy heuristic, not
  protection from a deliberate agent. Brain-mode code can encode data in arbitrary outputs; its
  results go to the external provider by design. Confidentiality requires standalone driver mode
  with all models local and no remote recipients. MCP docs include wording for the manuscript
  author; this task does not edit the paper or register real clients.
- Permanent tests cover renamed, rounded and combined CSV/Parquet copies, fresh read-time checks
  without artifact flags, readable describe/class/metric summaries, distinct-cell thresholds,
  same-row identity, renamed/coarse full-row facts (including scalars) and safe migration.
  Focused run: 14 passed. Final full suite: 101 passed, 1 skipped in 421.09 s; Ruff,
  wheel/resource checks and installed-wheel stdio discovery pass. M7 remains pending.

## 2026-10-07 — Review fixes R-MCP1/R-MCP2

- Full-row hashes alone cannot match a table with omitted columns. The private SQLite index stores
  salted cell hashes and row identities as well as normalized full-row hashes; intersections must
  resolve to the same source row. Column names are metadata; plaintext cells are not stored.
  Numbers use six significant digits. Source registration and split partitions are indexed.
- Table collection records copied-row flags; MCP reads recheck legacy artifacts without flags.
  Runtime full-row facts are rejected before Navigator extraction. Legacy full-row facts refuse
  guarded MCP use. Migration requires unchanged source files; corrupt stores fail closed.
- Report JSON reads remove embedded stdout/stderr, leaving full diagnostics local. Reports always
  state external agent file access as unknown (outside MLCA), including a trust-boundary report.
- Claude project permission previews cover registered source paths, private state, actual/default
  user-data folders and generated evidence copies. Bare Bash/PowerShell denies supplement human
  command prefixes, which alone miss absolute executables, -p arguments and wrapper commands.
  Claude Code 2.1.292 syntax follows its official permission documentation. Only --yes merges
  project settings, preserving existing denies and unrelated values after a mode-0600 backup.
  Other clients receive prose on stderr; their JSON registration output stays parseable.
- These settings are recommendations, not authentication or proof of client file access. Native
  tools/other filesystem MCPs can bypass MLCA; a separate OS boundary or MCP-only client is needed.
  Copied-row detection cannot prove anonymity: transformed data, labels, figures and small-group
  summaries can disclose observations. Confidential work uses local standalone driver mode with
  no external agent receiving study outputs.
- The author approved supporting actions and custom after completion on 2026-10-07, superseding
  the historical next-only decision. Fallback appends unrun supporting actions after primaries;
  completed events offer next first, supporting actions and scoped custom. Primary proposals after
  completion are refused, so alternatives still branch before the primary step. Supplementary
  steps preserve checks and generations; fit, scope and test-exposure controls still apply.
  No live models, original-data runs or real client registration.

## 2026-10-06 — Author instructions and scope

- P0–P8 implementation is authorized. Tests and smoke/full-cycle/live runs are deferred by the author;
  plan completion criteria remain unverified. Test source and fixtures are also deferred.
- P9 remains outside scope. No remote or publication. D1–D7 retain plan defaults; D8 is survival.
- Secret configuration uses environment variable names only (section 7.6 takes precedence over section 0).
- Draft templates are functional structural content, not approved scientific protocols.

## 2026-10-06 — Enforcement and reproducibility limits

- Hash chaining includes a separately cached head digest to detect last-line edits and truncation against
  that cache. A user controlling both files can rewrite them: tamper evidence is not an external signature.
- State replay is pure. Script verification is separate, uses a new environment and run folders, and
  reports mismatches. It never changes historical steps or represents fresh LLM generation as replay.
- Linux isolation binds only declared data and required runtime/library paths. If bubblewrap exists but
  cannot establish isolation, execution fails; it does not silently downgrade. Level B requires explicit
  project opt-in and is not a security boundary against malicious Python/native code.
- chmod prevents accidental writes, not writes by the owning user. Hash checks detect subsequent changes.
- fit records are checked against engine-known training indexes, not accepted by partition label alone.
  Static checks require the fit wrapper, but arbitrary generated/native code can evade instrumentation.
  This is a methodological check, not a proof of all preprocessing semantics.
- Test unlock is bound to the frozen split and branch. Branching cannot restore secrecy to data already
  seen by a person or provider. Unlocks and reruns remain visible in the project-wide log.
- Payload categories prevent intentional sample-row attachments; arbitrary user text, scripts, errors
  or figure labels may contain sensitive information. Redaction and bounded payloads reduce this risk;
  privacy guarantees do not extend to unrestricted free text.
- Unknown prices remain unknown; cost budgets require configured pricing or a per-request upper bound
  for real providers. Fake/local providers can use explicitly configured zero-cost bounds.

## 2026-10-06 — Implementation details

- Analysis runtime source is snapshotted into each project and installed as a small independent package,
  rather than an editable installation of the entire harness. This keeps provider code out of execution.
- Freeze operations use split-specific locations/keys, allowing histories to share immutable artifacts.
  Reported encryption is randomized; script replay compares regenerated split manifests rather than
  ciphertext hashes. Built-in report/inventory steps use consistency checks; ordinary scripts are rerun.
- A package-lock mismatch after branch checkout refuses execution. Restore the branch's recorded
  environment before continuing; the engine never silently substitutes a later dependency set.
- Only explicitly opted-in weaker execution is allowed without bubblewrap. No tests have established
  this host's namespace support yet.
- P2/P8 draft template structures were generated together; the survival content is finalized structurally
  in P8. Phase commits describe implemented source, not validated milestone completion.
- Request envelopes are transactionally persisted; usage/egress JSONL are recoverable projections.
  Unknown/in-flight usage reserves the configured upper-bound cost. HTTP framing is not captured.
- Report rebuilding also needs the frozen template snapshot and request sidecars; these are part of
  project evidence, in addition to event records and step artifacts.

## 2026-10-06 — Final source review

- Frozen runtime source and per-step package snapshots are recorded and hash-checked. Reproduction
  builds separate environments for each historical package snapshot and uses the frozen helper source.
- Inference redaction recursively handles strings instead of modifying serialized JSON syntax.
- Execution wall time, process compute time and model latency are reported separately; these overlap
  and must not be blindly added. Human decision counts are recorded, not estimates of human work time.
- Broad adapter/callback payload boundaries use Any annotations; persisted contracts use Pydantic.
- Static checks completed: Ruff lint, Ruff formatting and Git whitespace checks. No application modules,
  analysis scripts, UI sessions or tests were executed for validation.

- Runtime failure messages sent for Worker repair are reduced to exception type and script line when
  sample-row egress is disabled. Full diagnostics stay local; recap prompts receive event metadata only.

## 2026-10-06 — Startup corrections after external review
- Added postponed annotation evaluation in branches.py, preserving the existing Branches.list API.
- Renamed the TUI readiness helper to _can_act to avoid overriding Textual's internal _ready method.
- A focused startup check also found run_action overriding Textual's asynchronous action dispatcher;
  renamed the session worker helper and its call sites to run_session_action.
- Focused verification for these fixes passed: CLI --help and --version; headless Textual welcome-screen
  mounting, guarded choice/next actions without a project, and keyboard quit. No models or datasets used.
- No permanent test suite was added. Full-cycle, scientific, provider and broader UI validation remain deferred.

## 2026-10-06 — D5 resolved: logo
- The author supplied the MLCA logo (robot head between two neural networks, "Machine Learning Copilot
  Agent" lettering). It is used for the terminal banner (Braille art generated from the figure only) and
  as a grayscale `assets/logo.png` for later desktop use. The source image is the author's own; no
  third-party attribution applies.
- Banner kept deliberately small (10 rows, no tables or tool lists), unlike Hermes' startup panel.

## 2026-10-06 — Functional review: test authorization and F3
- Prompt 01 authorizes permanent offline unit/integration/TUI tests, including slow runs; it overrides
  the earlier test deferral for these fixes. Real-provider and original-data runs remain outside scope.
- Output checks accept an any-of list as well as the original action/output form. Primary actions must
  be covered by event sub-goal checks; supporting actions cannot supply required completion evidence.
- Both draft templates cover alternate split, feature and model actions. Supporting target counts
  no longer copy schema-audit fact candidates. Scientific template content remains DRAFT.

## 2026-10-06 — Functional review F4
- Branch and checkout re-check current event sub-goals before materialising views.
- Fallback considers default actions and remaining primary alternatives. Exhausted parameterised
  actions explain that different parameters are needed; an exhausted parameterless event explains
  that a custom instruction or branch is required.
- Prompt 01 conflicts: completed events must have no fallback action options, but its branch test
  requests an alternative after the completed model step is re-checked. Pending author clarification,
  completed events retain next; alternatives are tested when model completion remains open.

## 2026-10-06 — Functional review F5 and branch clarification
- Author confirmed: completed events keep next; branch recovery tests and unfinished-event alternative
  tests are separate. This resolves the conflicting F4 acceptance wording.
- Init resolves target/duration/event columns against inventory before creating project folders.
  Exact names win, then unique case-insensitive names; CLI/TUI ask on unresolved interactive input.
  Non-interactive errors list the columns. Original brief answers are preserved separately.
- Existing survival briefs use target for duration; that value resolves both structured fields.
  Old projects accept verbatim columns only on exact inventory matches. Onboard evidence, role context
  and the facts panel show structured columns so author confirmation covers the resolution.

## 2026-10-06 — Functional review F6
- Session records are lazy: only the first mutation starts a session, and only started sessions end.
  Branch operations explicitly start their session before their direct store appends.
- Store caches parsed records, offsets, ids and branch heads; only appended bytes are parsed on growth.
  File replacement, shrinkage, same-size metadata changes or checkpoint discrepancies force full verification.
  Session open and explicit verify always inspect the entire log. Hashes are tamper evidence, not signatures.
- Session replay is cached by branch/head id and invalidated on emits; direct appends also change the key.

## 2026-10-06 — Functional review F7 and scientific refusal wording
- Welcome/workflow bindings now belong to their screens; Tab/XOFF aliases are removed.
  Session output and subscribed records use readable summaries rather than raw option dictionaries.
- Input validation occurs before step folder creation. Tamper diagnostics identify the preceding
  modified line or last-line checkpoint mismatch; full verification retains all integrity checks.
- Confirmed repository .cache contained only uv; preserved downloaded dependency entries in uv's
  standard external cache for offline testing, then removed .cache. Repository-local caches are forbidden.
- Fit-stage requirements are unchanged. Refusals direct read-only work to validate/interpret;
  fit index mismatches report expected/received counts while retaining exact index-hash enforcement.

## 2026-10-06 — Permanent functional suite completed
- Reviewer-derived synthetic fixtures drive real separate analysis environments, both available
  sandbox levels, script replay, test lock cleanup, branch recovery and headless Textual checks.
- Dependency priming occurs before tests. The suite itself sets UV_OFFLINE=1. Its external scratch
  root avoids /tmp quotas and every project fixture cleans its immutable step directories afterward.
- Generated subprocesses limit BLAS/OpenMP numerical threads to one for bounded small-step overhead
  and deterministic execution. This does not change fit partition or scope requirements.
- Branch replay clears inherited pending options; the TUI displays exhaustion notes as readable text.
- Full suite: 40 passed in 263.43s. Reverting F3 yielded KeyError: 'action'; reverting F6 yielded
  Unexpected full log reread. Both fixed versions were restored before the passing full run.
- Prompt 02 may now proceed: distribution files and local dry runs only; no publication authorization.

## 2026-10-06 — Distribution A: artifact and browser view
- Version metadata is dynamic from src/mlca/__init__.py. pyproject.toml remains the distribution-name
  authority; packaging/NAME is a generated mirror for wrapper/resource consumers, not a second choice.
- Package metadata labels its only current URL as the legacy implementation, since the v2 public
  repository is undecided. Contributor names and final source URL can be updated before release.
- Wheels contain both templates, styles, the derived logo/banner and mlca_runtime; source artwork is
  excluded. The LICENSE placeholder remains explicitly unlicensed; release guards are added in C.
- mlca web uses textual-serve's documented Server API and binds 127.0.0.1 only. The extra is optional
  for users and included in dev dependencies so its offline smoke check always runs.
- Three distribution checks pass: missing-extra refusal, HTTP start/stop and fresh uv-tool wheel install
  with version, JSON doctor and terminal banner. No publishing occurred.

## 2026-10-06 — Distribution B: platform execution
- Scrubbed processes use a per-step temporary home/temp directory, os.pathsep and runtime-derived
  read roots from the base interpreter, sysconfig and analysis environment. Windows receives only
  whitelisted SystemRoot/WINDIR values for interpreter/DLL loading, never arbitrary user environment.
- Linux namespaces mount that temporary home separately. The level-B audit hook no longer grants
  blanket access to the host's /tmp; path comparisons normalize case on Windows and handle drives.
- Level B remains opt-in. Doctor explains macOS/native Windows limitations and recommends WSL2 with
  bubblewrap for Windows users who require level A. Native platform execution awaits the CI matrix.

## 2026-10-06 — Distribution C: gated release files
- CI runs Python 3.11/3.13 on Linux/macOS/Windows, installs bubblewrap on Linux, primes dependencies
  before an offline suite, and checks wheel resources. Ubuntu's ephemeral CI runner enables user
  namespaces when its AppArmor restriction would otherwise prevent level A; local host settings are untouched.
- Release depends on the CI matrix, matching version tag, a non-placeholder licence and the author-set
  PACKAGE_NAME_APPROVED variable. All publication jobs use environment release; the author must
  configure required reviewers in GitHub before any release. OIDC handles PyPI; npm uses provenance.
- Homebrew updates are conditional on HOMEBREW_TAP and need a tap-scoped token to propose a PR.
- Workflow YAML syntax and local negative/positive metadata guards pass. actionlint and act are not
  installed here, so actionlint validation and act -n were not run. No workflow was triggered.

## 2026-10-06 — Distribution D: generated wrappers
- POSIX and PowerShell installers offer consent for Astral uv bootstrap, version pinning, upgrades and
  optional PATH modification. They print isolation guidance; they never run sudo or add telemetry.
- npm has no installation hooks. Its small launcher finds uv, pins the Python artifact version,
  forwards arguments/status/signals and never downloads uv. Windows tests create a genuine fake uv
  console executable from a local fixture wheel rather than invoking untrusted command strings.
- sync_versions.py reads the two authoritative sources, refreshes packaging/NAME and generates npm
  identity/licence and standalone installers. Homebrew's renderer reads NAME and the release sdist hash.
- Installer dry runs, Node forwarding/status/missing-uv/signal checks, intended npm-pack file listing,
  wrapper identity checks and Ruby formula syntax pass. PowerShell parsing is skipped because pwsh
  and PSScriptAnalyzer are unavailable; shellcheck is unavailable, but sh -n passes.

## 2026-10-06 — Distribution E: documentation and final verification
- Install/release guides distinguish prepared channels from publication and explain all OS levels,
  removals, config/data/key locations and author-only registry/environment/tap setup.
- Generated formula previews are excluded from the sdist to avoid embedding an archive's own hash
  in its source. The template remains included; release rendering uses the built sdist SHA256.
- Artifact identity validation requires a common lowercase unscoped name for Python and npm.
- Text resource/log/script reads and writes use UTF-8 explicitly; CLI streams and analysis subprocesses
  also use UTF-8 so Windows locale defaults cannot corrupt Braille artwork or Unicode evidence.
- Test helpers have their own module; nested conftest files no longer collide during full collection.
- Final suite: 54 passed, 1 skipped in 227.66s; the skip is unavailable PowerShell parsing/analyzer.
  Node reports 4/4 passing; shell/Ruby syntax, wrapper sync, wheel install, web smoke, YAML and release
  guard checks pass. shellcheck, actionlint, act and native macOS/Windows execution are unavailable here.
- D1 licence and D3 public name remain blockers; publishing additionally needs the one-time external
  infrastructure setup documented in releasing.md. Only local commits/builds/dry runs were performed.

## 2026-10-06 — D2 content v0.2.0 and MCP direction
- Template content written (reviewer, at the author's request), short by rule (docs/templates.md).
  Concrete defaults to review per study:
  - classification: 60/20/20 stratified split, seed 42; logistic baseline and gradient-boosting
    alternative; ROC AUC primary; Youden threshold on validation; 1,000-resample bootstrap CI on test;
  - survival: random split; Cox and penalised Cox; C-index primary.
- MCP docking adopted as the integration path for external agents (plan_mcp.md). Brain mode is the
  default for MCP; driver mode remains for standalone use. Human-only decisions (confirm, unlock test,
  package approval) are never exposed as MCP tools. Implementation starts after the missing core
  invariant tests.

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

## 2026-10-07 — MCP M6 implementation decisions

- Registration previews never execute. `--yes` is the explicit consent flag; existing target
  configs and overwritten skill files are backed up first. Claude/Codex/Hermes flags were
  checked through installed CLI help; OpenClaw/Cursor formats use official documentation.
- The plan's generic OpenClaw snippet was superseded: OpenClaw's native registry is
  `mcp.servers`, with `mcp set <name> <json>`. Hermes uses its verified `mcp add` CLI and
  documents equivalent YAML. Codex/Hermes/OpenClaw support user registration in this helper;
  project scope is refused rather than silently targeting a different scope. Claude/Cursor
  support both. Project registration pins an absolute study path.
- Claude backups honor its `CLAUDE_CONFIG_DIR/.claude.json` override; default is
  `~/.claude.json`. No real client configuration was inspected or changed during this work.
- The optional 38-line skill is copied only with `--yes --with-skill` to supported clients,
  and is included in the wheel. Generic JSON output is valid JSON and has no automatic target.
- Doctor queries list commands with bounded timeouts and returns presence only, never
  config contents. The wheel validation used an isolated PATH with no installed client CLIs.
- Additional review fixes: MCP checkout returns a compact overview rather than Session's
  internal state; new briefs redact known environment credentials before persistence while
  retaining other verbatim answers; unexpected submitted-step failures freeze evidence.
  Parquet row metadata and an 8 MiB table-file cap avoid reading oversized summary inputs.
- ClientInfo is attribution, not authentication. A same-user unrestricted shell can invoke
  the human CLI; claims and agent guide state this boundary. Arbitrary generated artifact
  semantics are not proved by table/image bounds.
- M7 belongs to the author and requires actual client/provider runs. It is not substituted
  with SDK tests; no live provider or original-data run was attempted.

## 2026-10-07 — D1/D3 resolved; authorized PyPI beta

- The author chose CC-BY-NC-ND-4.0 and the package name `mlca`, and authorized one upload of 0.2.0b1 to PyPI. The official legal code is retrieved from https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt.
- GitHub pushes, new remotes and npm publication remain unauthorized. The VM guide was committed separately first (`45344a5`).
- Release tooling formerly refused prereleases. It now supports stable/a/b/rc versions; npm uses SemVer `0.2.0-beta.1` with a separate Python pin `0.2.0b1`. Beta installers default to the explicit beta; stable installers retain latest-stable behavior.
- The Homebrew formula is rendered after building, using the actual sdist SHA256; it is excluded from the sdist to avoid a circular hash. No Homebrew channel is published.
- Beta gates: 106 passed, 1 skipped (PowerShell unavailable), 446.34 s; focused distribution tests 13 passed/1 skipped; Ruff lint/format pass. Twine and the 179-entry wheel resource check pass.
- Isolated wheel walkthrough: install/version/doctor, synthetic generation and interactive init, Claude project-scope/skill preview without writes, official stdio discovery of 14 tools, and a working bubblewrap namespace probe. No native client was registered and no model was called.
- Credential-pattern scanning covers all repository files, including local git/venv files, and unpacked distributions; no PyPI-token-shaped content was found. The credential file is only read by the authorized publish command.

## 2026-10-07 — PyPI name rejection

The authorized upload was attempted once after all gates passed. PyPI returned HTTP 400 on the first wheel: the name `mlca` is too similar to an existing project. Nothing was accepted. No invalid-token error was returned, but this response alone is not a separate credential-validation test. The token was neither displayed nor persisted and was read only by the authorized command.

D3 is author-approved but blocked by registry validation; a replacement name or resolution with PyPI is required. No retry under an unapproved name, new version, tag, npm publication or remote operation was performed. Post-upload installation is deferred. The account-wide credential has not been deleted or replaced: no project was created, and it was not inspected again.

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

## 2026-10-07 — Author-approved replacement distribution

The author chose `mlcagent` for the 0.2.0b1 PyPI beta, superseding `mlca` and the suggested legacy name. The executable, imports, MCP tools and state folders remain `mlca`. Wrapper identities, installers and metadata now use `mlcagent`. The earlier rejected upload is retained above as historical evidence. One beta PyPI upload is authorized after release validation; GitHub pushes, new remotes and npm publication are not authorized.

## 2026-10-07 — Final release regression check

The first complete P10/replacement-name suite ran 135 passed, 2 failed, 1 skipped in 591.85 s. Both failures were the completed-event supporting-action refusal explanation: the new invalid_options wrapper discarded the controlled engine reason. The wrapper now preserves MlcaUserError explanations while retaining generic schema-error messages and the category. The strict refusal is unchanged. A full suite rerun is required before publication. Missing benchmark sequence evidence is excluded from agreement statistics and counted as unavailable.

## 2026-10-07 — P10 and mlcagent beta release gates

P10.1–P10.7 are implemented. Final full offline suite: **137 passed, 1 skipped in 603.43 s** (PowerShell unavailable); supporting-action/failure targeted subset: 20 passed. Ruff lint/format, approved-name/version guard, wrapper synchronization, build/Twine and 186-entry wheel resource checks pass. The final isolated HOME/XDG wheel walkthrough passes install/version/doctor, synthetic init, Claude project/skill permission preview without writes, bubblewrap namespace probe and stdio discovery of all 14 tools. No live models, original anemia data or native client/OS validation were performed. The authorized PyPI upload as `mlcagent` 0.2.0b1 follows; npm/GitHub operations remain unauthorized.

## 2026-10-07 — mlcagent beta published

Published wheel and sdist for [mlcagent 0.2.0b1](https://pypi.org/project/mlcagent/0.2.0b1/) from local source `16bcc72`. PyPI accepted the token and both artifact hashes match. No GitHub push, npm publication or new remote occurred. Fresh-index install/version/doctor/14-tool verification passed. The frozen beta README retains an overlooked historical Status paragraph about the rejected mlca name and the old test count; source README Status is now corrected for the next release. No artifacts are replaced or additional releases uploaded. Project-scoped token replacement and removal of the account-wide token file remain an author account step; the credential is not reopened.

## 2026-10-07 — Published-beta verification

[PyPI release](https://pypi.org/project/mlcagent/0.2.0b1/). Fresh PyPI verification used an empty temporary HOME/XDG and uv cache: `uv tool install mlcagent==0.2.0b1`, `mlca --version` (0.2.0b1), `mlca doctor --json` (level A capability; execution must confirm isolation), and `mlca mcp doctor` (14 tools) all passed. Published wheel/sdist SHA256 hashes match the scanned release artifacts. Local tag `v0.2.0b1` points to release source `16bcc72`; no push. P10 is complete, while M7, real providers/data, and native macOS/Windows remain pending. The beta description contains an overlooked historical README Status paragraph; it is corrected in source for the next release, with no second upload. Token rotation to a project-scoped token and removal of the account-wide file remain an author account step; the file was read only by the publish command.
