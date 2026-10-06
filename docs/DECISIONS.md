# Implementation decisions

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
