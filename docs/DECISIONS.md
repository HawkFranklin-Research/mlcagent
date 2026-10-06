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
