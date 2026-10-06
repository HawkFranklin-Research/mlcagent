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
