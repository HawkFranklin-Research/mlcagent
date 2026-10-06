# Event log and recovery

`.mlca/log/events.jsonl` contains validated records. Each has a ULID, UTC timestamp, actor, session,
branch ancestry (`parent_id`), optional event/step context and a previous-line SHA256. A FileLock
serializes durable appends. A separate head checkpoint detects last-line changes and truncation.

`parent_id` follows the branch; `prev_hash` follows physical file order across all branches.
Replaying a branch ancestry is pure: no clock, model call or filesystem read. `state.json` and
`branches.json` are caches. Current checkout is recovered from BranchCheckedOut records.

A partial write or interrupted checkpoint update fails verification. Do not remove the checkpoint or
rewrite the log to bypass that failure. Preserve both and investigate before recovery. Hash chaining
provides tamper evidence relative to the stored head; it is not an externally signed immutable archive.

Request evidence is transactionally committed to `.mlca/requests/<request_id>.json`, containing one
usage record and one egress record. `usage.jsonl` and `egress.jsonl` are replaceable materialized views.
Pending requests reserve their budget before transmission. Requests interrupted by a crash remain
pending/unknown, not falsely labelled free. Payload files are optional and controlled by privacy settings.

`mlca replay` rebuilds state. `mlca replay --verify` is a separate, explicit execution command that
creates a fresh analysis environment, reruns historical scripts and compares nonfigure hashes and
metric manifests. It performs no new LLM generation. Floating-point/platform/library nondeterminism
may produce mismatches; these are reported rather than hidden. Built-in report steps are checked for
evidence consistency; split operations are regenerated using the recorded seed and parameters.

## MCP records and pending work

Actors include `agent:<client>/<version>` alongside historical engine/model/user actors.
`ApprovalRequested` freezes request context; `ApprovalResolved` records the human decision.
`ScriptRequested` persists a redacted work order, hash and attempt number. `ScriptWritten`
identifies its Worker/agent source. A pending external step can resume after reopening.
Abandoning a step records StepFailed and freezes its evidence. Branches cannot erase exposure.
MCP usage envelopes count external tools separately from model requests and omit unavailable
external inference costs; read-only MCP calls write request evidence, not SessionStarted log noise.
