## Work order 05 — 16 October 2026 (baseline validated; batch-01 ready)

Work order 05 replaces the earlier Part B procedure. Round 2 is closed, not
continued: experiments dae6775 preserves its three failures and interrupted
energy run. No new-model call has occurred during baseline preparation.

Completed local changes, in required order:
- L-0002 rails-0.3 design pass: 5ded618 (24 generic instruction rails).
- E1–E4 metric aliases/shared defaults, bounded model calls and unsupervised
  action wording: d48b0f8. E5 approved setup value inventories and reasoned,
  validated label spelling maps: 9026276.
- E6 fitted column names and E7 training group retention: bf8814b.
- Researcher-only development leakage fields: 99b415b; external scorer:
  experiments 4efef07. Unknown evidence stays unavailable.
- Shared request pacing, unlimited-budget configuration and explicit ablation:
  c448e56. Parallel/resumable queue: experiments eb70bd3; six focused controller
  and leakage tests pass; twelve focused engine control/rails tests pass.

The initial full suite exposed an optional-deadline adapter compatibility defect
(389 passed, 18 failed, 1 skipped); all affected regressions passed after the fix
(44 tests). The fresh full offline gate, partitioned across four isolated pytest
processes, passed **408 tests, 1 skipped**, zero failures/errors (slowest partition
379.11 s). Experiments tests: **18 passed in 11.31 s**. Ruff and diff checks pass.
Logs/XML: /home/prime/.cache/mlca-05-parallel-gate/.

Exact next step: launch batch-01 (if no batch.json exists), otherwise inspect its
live state and controller before using --resume. Command from experiments:
`../mlca-revized/.venv/bin/python scripts/run_batch.py --batch 1 --out
bench/dev-loop/batch-01 --model deepseek/deepseek-v4.1-flash --concurrency 6`.
Use the fresh baseline commit and controller eb70bd3;
all twelve DEVELOPMENT entries, six concurrent studies, exact model
`deepseek/deepseek-v4.1-flash`. Paid calls are authorized without a spending
ceiling; use OPENROUTER_API_KEY without printing or persisting it. Parameters
are recorded in experiments bench/dev-loop/PARAMETERS.md. No model substitution.

Status: O1–O7 implemented for this baseline; O8 batch loop ready, acceptance
not attempted; O9 freeze not started.

Batch controls: one large table at a time; 5,400 s/study, 300 s/model call,
300 s default script timeout; no additional memory limit; full input tables.
After each batch report all failures, make consolidated generic repairs between
batches only, and rerun failed tables. Acceptance K=3 then rails ablation;
stop at acceptance+ablation or ten batches/five days and prepare Part C.

Held-out tables remain untouched; paper read-only. No freeze, version bump,
release, tag, push, remote or upload. CLI automatic OpenRouter sign-in remains
an acknowledged later usability item, not part of this work order.

---

## Work order 04 Part B — 16 October 2026 (in progress)

Part A is complete at 32530ae: 380 passed, 1 skipped (PowerShell unavailable).
The author authorized the live rails loop while sleeping. Only openrouter/free
is used for Navigator and Worker, at 16 requests/minute, sandbox A required.

Round 1: twelve fresh setup attempts, zero completed workflows, twelve requests,
17,340 input / 44,055 output / 39,694 reasoning tokens as provider-reported,
and $0 reported cost. Eleven failures exposed the engine's inconsistent setup
schema; one exhausted its output budget. No Worker script ran. Immutable raw
attempts and hashed curated evidence are in experiments commit e74b799 under
bench/dev-loop/round-01/. Reviewed classifications are separate annotations.

B-0001 fixes the advertised schema/repair path and failed-setup accounting;
RL-0001 is a candidate generic setup-brevity instruction. Full offline suite:
**387 passed, 1 skipped in 1197.87 s** (PowerShell unavailable); Ruff passes.
Local commits: engine fix c5ea681, instruction rail 900bd07. Round 2 starts
from this tested source with rails-0.2. Acceptance K=3 has not been attempted or reached. See rails/LEDGER.md
and rails/REVIEW.md. Do not treat development failures as frozen measurements.

Held-out tables remain untouched. No paper edit, installed-tool refresh, freeze,
package version change, tag, publication, remote operation, push or upload.
Automatic CLI OpenRouter onboarding is still a later usability item.

---

## Work order 04 Part A — 16 October 2026

A1/A2 are committed (0bdeb79, 6c0576e); external unsupervised/inference scorers
are in experiments commit e7eef1e. A3 autonomous execution, A4 decision windows
and A5 sourced autonomy metrics are implemented locally. Full offline validation:
**380 passed, 1 skipped in 1189.07 seconds** (PowerShell unavailable); Ruff and
whitespace checks pass. A3 commit fb8abf2; A4 commit 6c7d3aa; A5 is this update.

**Author boundary (updated):** the author subsequently authorized Part B while
sleeping. Part A validation is complete; finish its local commits before the live loop. It has
not started yet. Its account metadata check reports 1,000 free requests remaining. No live model inference
calls, held-out inspection, freeze, version bump, installed-tool refresh, push,
upload, release, or paper edit in this continuation. Existing untracked datasets
and author work orders remain preserved. CLI automatic sign-in is deferred.

---

# Current work order status — 14 October 2026

**WP1–WP7 completed locally; stopped after package 7.** P17 E1/E2 and the P18 packages
are implemented. E3 was deliberately not built. Work remains on `master`; the existing remote
HawkFranklin-Research/mlcagent was not changed. No measurement freeze, tag, version bump,
installed-tool refresh, live model call, push, upload, publication or paper edit occurred.

Local phase commits before WP7: code 829f2f1 (WP1), f720622 (WP2), bbc72fd (WP3),
2ea2506 (WP4), cd498a3 (WP6); experiments f85fc4d (WP5).

**Tests:** final code suite **296 passed, 1 skipped in 1146.03 s** (PowerShell unavailable).
Ruff and diff checks pass. Experiments suite: **7 passed in 10.47 s**, including export audit
regressions. Repeated deterministic preparation retained input/output hashes and expected counts.

**Offline reference acceptance:** all seven attempts finished with zero model requests.
S1 core completed but its four custom instructions were not achieved. Six S2 attempts failed:
four interpretation timeouts (RNA/proteome ER and PR), and two HER2 bootstrap NaN/strict JSON
errors. These are retained development findings, not successful full protocol runs or measured
AI results. Submitted custom instructions remain verbatim, including refusals. One proteome ER
attempt was interrupted and resumed after a question-review performance correction; this is
explicitly labelled, not counted as a fresh measured repetition.

Curated evidence, hash/exclusion audit and summary are in the experiments repository:
`bio-bench/acceptance/2026-10-14/`. Exports are evidence bundles, not standalone replay archives.
The sub-agent's timestamped `INTERIM_REPORT.md` is preserved as the interim snapshot.

**Next, only on subsequent author instruction:** live driver/brain smoke (MB6), reference
bootstrap and interpretation/performance follow-up, scientific finalization, measurement freeze,
approved preregistration and measured repetitions. Activity reconciliation still needs the real
Activity CSV. Draft cards and placeholder scientific instructions are not final methods.
Never stage `*.local.md`, local path configuration, prepared inputs or private/environment data.

---

## Historical status

# P16 and revision-cut status — 13 October 2026

P16.1–P16.4 and metadata backfill implemented; Navigator failure recovery (P14.6) implemented.
Full offline working-tree suite: **245 passed, 1 skipped in 678.51 s** (PowerShell unavailable). Ruff lint and formatting pass. The isolated selective P16/P14.6 candidate passed 34 tests, independently of the other uncommitted work.
Pending: real Activity CSV reconciliation, author-authorized live smoke, post-freeze P14/P15 work.
See [P16 accounting](P16_ACCOUNTING.md). Pre-existing changes remain separate; no remote operations.

# MCP/TUI alignment acceptance — 2026-10-13

MX1–MX6 implemented in ordered local commits. Full offline suite: **202 passed, 1 skipped in 719.16 s** (PowerShell unavailable). Ruff lint/format pass. Installed source refreshed after MX5; final refresh includes MX6. No live model calls, computer controls, remote pushes or beta 3 publication. Public beta 2 is unchanged; local development source still reports 0.2.0b2. Master and browser plans remain untouched.

The synthetic SDK, CLI and Textual tests cover human card routes/refusals, validated proposals and attribution, live updates while awaiting scripts, phase order and progress callbacks, bounded privacy/accounting views and brain-mode metrics. Native real-client M7 remains an author-run check.

## Beta 2 release validation — 2026-10-13

## Beta 2 published and beta 1 yanked — 2026-10-13

Published [mlcagent 0.2.0b2](https://pypi.org/project/mlcagent/0.2.0b2/) using the authorized upload token; both public artifact hashes match. Fresh isolated HOME/XDG PyPI install, version, doctor and 14-tool MCP verification pass. Beta 1 is yanked (both files), verified in release management and public PyPI JSON. Local tag v0.2.0b2 records release source bdc2f376ef2b9b2848d5f5ed5b272ee9aad2a311; global mlca was refreshed to 0.2.0b2. No GitHub/npm push or publication occurred. Master and uncommitted browser plans remain untouched.

Final suite: 193 passed, 1 skipped in 647.09 s; lint/format, metadata, wrappers, Twine, wheel resources and isolated synthetic init/permission-preview pass. Real OAuth/model/data validation and OpenAI registration remain pending. The token was read only by the publish command and never displayed, copied or committed.


Full offline suite: **193 passed, 1 skipped in 647.09 s** (PowerShell unavailable). Ruff lint/format, release metadata and wrapper checks pass. Rebuilt wheel/sdist pass Twine and the 206-entry wheel check. Isolated HOME/XDG install, version/doctor, synthetic initialization and 14-tool MCP discovery pass; Claude registration/skill preview writes no configuration. No live models, real OAuth authorization or original-data study was run.

PyPI 0.2.0b2 upload and subsequent beta 1 yank are authorized; publication verification follows.

## P11 guided TUI — 2026-10-13

P11.1–P11.7 implemented on native-onboarding in local sub-phase commits. Numbered clickable cards
include engine-generated study/confirmation/navigation decisions; unresolved onboarding defers
Navigator calls. Visible progress, branch journey, raw-log toggle, observed model status, explicit
connection/quota checks, queued switches, durable bench model locks, secure keyring references and
registration-gated official ChatGPT Responses integration are implemented. Setup publishes .mlca
atomically; old incomplete setup can be archived with confirmation, never silently deleted.

Focused pilot reaches data using cards only. Fake provider/auth/quota/clock, canary, model switch,
replay and relocated-environment regressions pass. Synthetic screenshots: docs/screens; capture
script: scripts/capture_tui.py. Full suite: 193 passed, 1 skipped in 647.09 s. No live model or OAuth exchange,
real datasets or native macOS/Windows validation performed. OpenAI registration remains an author
step; its dynamic-registration option is not enabled by this implementation. Account-wide quota,
unknown monetary plan cost and upstream router model identity are not invented.

## Native OpenRouter sign-in — 2026-10-13 (unreleased)

Implemented browser/headless PKCE S256, state-checked loopback callback, expiry/single-use exchange,
secure OS keyring-only persistence and session-only TUI fallback. Model settings offer Start free
with OpenRouter and Sign out; CLI provides signin/signout. The free preset configures Navigator
and Worker without paid fallbacks, preserves optional roles/settings, and enables structured output.
Doctor reports local credential availability only. Documentation: docs/providers.md.

Verification: full offline suite **164 passed, 1 skipped in 609.33 s** (PowerShell unavailable).
The suite began before the final callback timeout/cancellation/redaction hardening; the final
focused auth/catalogue/onboarding suite passed **20 tests in 3.82 s** afterwards. Ruff lint/format,
CLI help, wheel build and 194-entry resource check pass. No real sign-in, OS-keyring write or
inference call performed. Native OS keyring integration and live OpenRouter authorization require
manual verification. Concurrent logo/welcome/main-table changes remain outside this commit;
master remains c6fabad. The published beta is unchanged.

# Implementation status — 7 October 2026

## Native onboarding branch — 12 October 2026

Implemented on `native-onboarding`, separate from frozen master and published beta artifacts.
File/folder browsing, explicit main/supporting tables, deferred study fields, plain-language dynamic
forms, role-aware provider settings, masked session-only keys, cached searchable catalogues/free
filtering and sourced pricing are implemented. Human study resolutions are included in intervention
counts; their wall decision time remains unavailable unless separately instrumented.

Final full offline suite: **152 passed, 1 skipped in 619.88 s** (PowerShell unavailable). Ruff lint and
format checks pass. Focused CLI/TUI/MCP/init/catalogue checks: 24 passed; study-resolution/screen checks:
5 passed; metrics/resolution/UI subset: 8 passed. The first broad run was 147 passed, 1 skipped before
the additional tests were included.

Native forms were exported and visually inspected at 120×45; UI tests also run at 100×35 and 80×30.
A deferred Study details screen passed a separate selection/save check. Screenshot artifacts are
local under ~/.cache/mlca-onboarding-screens, outside the repository. No real-provider completions,
original-data studies, public deployment or remote push were performed.

See [native onboarding](native-onboarding.md) for commands, session-key lifetime, supporting-table
limits and local installation refresh. New StudyFieldsResolved records require the updated native
code; compatibility means this code reads old single-table projects, not that the old PyPI binary
understands newly added record types. Existing project templates remain frozen.

The pre-existing README.md/plan.md edits and untracked web plans remain untouched/uncommitted.

## Current result

**Published beta:** [`mlcagent` 0.2.0b1](https://pypi.org/project/mlcagent/0.2.0b1/). Both files were accepted by PyPI with the author-provided token; public SHA256 hashes match the tested artifacts. Local release source: `16bcc72`.


**Latest work:** P10.1–P10.7 implemented with sourced metrics, usage imports and independent task-card benchmarks. The author-approved distribution is `mlcagent` 0.2.0b1; command/import remain `mlca`. Release validation passed (137 tests passed, 1 skipped). Both artifacts are published at [https://pypi.org/project/mlcagent/0.2.0b1/](https://pypi.org/project/mlcagent/0.2.0b1/); fresh-index installation and 14-tool verification passed. Older upload results below describe the rejected `mlca` name, not this release.


MCP M0–M6 and review fixes R-MCP1/R-MCP2/R-MCP1b are implemented. The author approved the supporting
action/custom-after-completion change, which is also implemented. Final validation of these
changes is recorded in the review section below. The historical M6 result was 81 passed,
1 skipped in 360.22 s, plus Ruff and installed-wheel discovery.
M7 is the manual author checklist in [MCP docking](mcp.md). No live models or original data
have been used. Earlier validation entries below are historical phase results.

## 2026-10-07 — R-MCP1b

- Index and match numeric cells at six/four significant digits, independent of column names.
  Table heuristics count min(3, returned column count) distinct matches in one source row;
  existing exact shared-column checks remain. Full-row facts ignore names/order as well.
- Version-1 indexes upgrade atomically using unchanged registered sources; sealed test data is
  never decrypted for migration. Failed upgrades preserve the previous index.
- Focused offline tests: **14 passed in 25.35 s** after the final scalar precision correction.
  They cover renamed/rounded/combined copies
  in CSV and Parquet, reads without flags, readable describe/class/metric summaries, thresholds,
  distinct source cells, coarse full-row facts and migration failures.
- **Final full suite:** `uv run pytest -q` — **101 passed, 1 skipped in 421.09 s**.
  The skip remains unavailable PowerShell analysis. Ruff lint/format (147 files), Git whitespace,
  wheel/sdist builds and resource checks (178 wheel entries) pass. Installed-wheel stdio doctor
  negotiates 2026-07-28 and discovers all 14 tools with isolated config/data and client-free PATH.
- README/MCP/security documentation and trust reports describe accidental/simple-copy detection,
  not resistance to a deliberate agent. Brain mode can encode data in outputs; confidential
  studies use local standalone driver models without remote output recipients. No paper edits,
  live model calls or client registrations were performed.

## 2026-10-07 — R-MCP1/R-MCP2 and supporting actions

- Private salted row fingerprints at registration/split; collection flags, CSV/Parquet read-time
  checks, full-row fact refusals and private-store execution probes. Tests distinguish copied
  head rows from readable describe summaries, reordered/shared-column projections, numerical
  rounding, same-row identity, corrupt/missing stores and legacy fact/artifact metadata.
- Report reads omit stdout/stderr; reports always state external agent file access as unknown.
  Claude permission previews and --yes backup/merge are tested without actual registrations;
  JSON snippets stay valid while other clients receive guidance on stderr. Trust boundary and
  derived-output disclosure limits are documented in README, MCP docs and the bundled guide.
- Author-approved menu changes offer primaries then unrun supporting actions. Completed events
  offer next first, unrun supporting actions and scoped custom. Primary proposals after
  completion remain refused, and supplementary steps preserve checks/generations. MCP tests
  cover count_target before/after audit_schema, accepted scoped custom, refused out-of-scope
  custom and next; a plain-driver fallback regression and historical branch tests remain.
- Initial focused privacy/helper/alternative suite: 21 passed in 57.27 s. Supporting-option
  unit/MCP tests: 5 passed in 13.31 s; plain-driver/branch/row-privacy regressions: 8 passed
  in 47.71 s. Intermediate full run: 92 passed, 1 skipped in 429.94 s.
- **Final full suite:** `uv run pytest -q` — **96 passed, 1 skipped in 396.58 s**.
  The skip is PowerShell analysis because pwsh/PSScriptAnalyzer are unavailable. Ruff lint and
  format check pass (147 files); Git whitespace check and bundled skill validation pass.
  Wheel/sdist build and resource checks pass (178 wheel entries). The installed-wheel stdio
  doctor negotiates 2026-07-28 and discovers all 14 tools with client-free PATH and isolated
  config/data directories. No actual clients were registered and no real model calls were made.

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

### Beta publication attempt — 2026-10-07

- D1 is resolved as CC-BY-NC-ND-4.0; D3 was author-approved as `mlca`. Release source is local commit `ac4bcc8`; incoming VM docs were committed separately as `45344a5`.
- Release gates pass: **106 passed, 1 skipped** (PowerShell unavailable), Ruff lint/format, approved-name/version guard, synchronized wrappers, wheel/sdist build, Twine checks and all 179 wheel resources.
- The built wheel passed the isolated HOME/XDG walkthrough: version, doctor, synthetic study init, Claude project/skill preview with no configuration writes, working bubblewrap namespaces and official stdio discovery of all 14 tools.
- **Publication blocked:** the single authorized `uv publish` attempt received HTTP 400 on the first artifact: PyPI rejected `mlca` as too similar to an existing project. No file was accepted; the public project JSON endpoint still returned 404 afterwards. This was a name-validation response, not an invalid-token response.
- There is **no published PyPI URL**. Registry acceptance requires a replacement author-chosen name or resolution with PyPI. A JSON 404 does not establish that a name can be registered. `mlca-agent` also returned 404, but its acceptance is unverified.
- Fresh installation from PyPI and the release tag are deferred until publication succeeds. No GitHub push, npm publication or remote creation occurred. No real client/model/original-data run was performed; M7 remains pending.

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

## 2026-10-07 — Published-beta verification

[PyPI release](https://pypi.org/project/mlcagent/0.2.0b1/). Fresh PyPI verification used an empty temporary HOME/XDG and uv cache: `uv tool install mlcagent==0.2.0b1`, `mlca --version` (0.2.0b1), `mlca doctor --json` (level A capability; execution must confirm isolation), and `mlca mcp doctor` (14 tools) all passed. Published wheel/sdist SHA256 hashes match the scanned release artifacts. Local tag `v0.2.0b1` points to release source `16bcc72`; no push. P10 is complete, while M7, real providers/data, and native macOS/Windows remain pending. The beta description contains an overlooked historical README Status paragraph; it is corrected in source for the next release, with no second upload. Token rotation to a project-scoped token and removal of the account-wide file remain an author account step; the file was read only by the publish command.

Installed-source checks: local uv tool refresh succeeded; mlca --version, installed-template resources,
headless new forms and mlca mcp doctor (14 tools) passed. A final UI-only blank-path guard prevents
empty data input from registering the current directory implicitly; the post-guard focused suite
passed 24 tests in 6.96 s. The full 152-pass/1-skip result above precedes that UI-only hardening.

## Existing-folder recovery — 2026-10-13

Native Create study now offers open/fresh/cancel when `.mlca` exists. A fresh attempt retains the
form and reserves a study-NNN subfolder without replacing old files; a missing project.yaml
marks the earlier attempt as not openable. CLI/MCP still refuse overwrite. Focused existing-folder,
onboarding and auth TUI regressions: **11 passed in 4.99 s**. Ruff passes. Installed source refreshed;
no full suite or real experiment rerun for this small UI change. Master and concurrent edits preserved.
