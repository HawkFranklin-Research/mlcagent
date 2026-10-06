# Execution and methodological controls

## Level A: Linux namespaces

Bubblewrap builds an isolated filesystem with read-only runtime/interpreter/library mounts and exactly
the declared input files. It mounts only the attempt folder writable; script and input declarations
are additionally rebound read-only. Network isolation is requested unless the action explicitly allows
network. No user home, test vault, encryption key directory or original dataset after split is mounted.
The audit hook supplies additional accidental-access checks. The runner kills the process group on
failure, timeout or interruption and caps captured output.

Availability of the executable is not proof the host permits namespace creation. A failed namespace
setup fails the attempt; there is no automatic downgrade. Synthetic level-A execution and private-path/network refusals are covered on this Linux host.
Trusted Python/system-library paths are visible read-only. This is not a formally verified sandbox and
does not limit CPU/memory/disk consumption beyond a timeout/output cap. Treat untrusted native code and
package installation as additional trust boundaries.

## Level B: explicitly opted-in trusted execution

Where bubblewrap is unavailable, execution is refused unless `sandbox.allow_level_b: true` is set.
Level B uses static checks, environment scrubbing, encryption and a Python audit hook, without filesystem
or network namespaces. Native extensions, dynamic code tricks and same-user processes may bypass it.
It is not an isolation guarantee against malicious generated code. Do not claim parity with level A.

## Test access

The engine, not a model script, partitions one registered table using random, stratified, group or time
splits. It preserves row IDs and hashes train/validation/manifest files. Test data are encrypted; keys
are engine-owned files outside the project. Test plaintext exists only during declared test-reading
steps and is deleted in a finally block. Interrupted/killed hosts may leave temporary plaintext: review
`.mlca/data/exposed/` before further work following a crash. Deleted files are not securely erased.

A user explicitly types `UNLOCK TEST` in the test event. Re-unlocks require reasons and are counted.
Project-wide exposure is included in reports even when a branch predates the unlock. Looping back or
fitting after exposure is rejected. Earlier raw-data inspections are not blinded: the lock concerns
subsequent step access, not what a person or earlier provider has already observed.

Raw-derived artifacts produced before the split are not automatically mounted into later analyses.
Static checks disallow direct fit calls and private/literal external paths. Runtime fit records check
training row-index hashes against the engine's frozen partition. This detects recorded validation/test
fits and direct fit calls in ordinary scripts. It cannot prove all transformations are leakage-free or
prevent fabricated instrumentation in malicious/native code. Schema checks, clinical target validity,
feature leakage and unit-of-analysis choices require expert supervision.

## Privacy and artifact integrity

Credentials are read from configured environment variables and scrubbed from request/log text. Analysis
processes receive an explicit environment, not inherited credentials. Model builders label payload
categories and reject sample-row attachments unless enabled. Free text, code, tracebacks and figure
labels may contain data: inspect them; category tagging is not a complete content-level privacy filter.
Runtime diagnostics sent for repair are reduced to exception type and script line by default; full
diagnostics stay local. Recaps use event metadata. Stored payloads are sensitive and should remain private. Egress hashes describe the normalized request
payload, not TLS/HTTP framing byte counts.

Step folders are chmod read-only after completion and recorded hashes are checked before reuse.
The owner can undo chmod; integrity checks detect subsequent content changes. Generated view changes
are reported and never silently overwritten. Workflow templates with `checks.py` are trusted code,
loaded by the engine, and must be reviewed before use. Dependencies installed by the user are trusted.


## Scientific guard rails

Steps in preprocess, features and model, including custom steps, must fit on the training partition
through `mlca_runtime.fit_record`. For read-only inspection, use validate or interpret. This requirement
keeps fit evidence attached to every step in a fit event rather than trusting an LLM's assurance.
`fit_record` requires the exact frozen training index, including order; mismatches report expected and
received row counts. Equal counts alone do not pass: this prevents fitting on substituted, validation
or test rows. Instrumentation and audit hooks cannot prove the semantics of arbitrary native code.

## MCP boundary

The MCP transport is local stdio. Every connected client is an agent principal; confirmations,
test unlocks and package approvals refuse agents inside Session, not just in the tool schema.
Human resolutions validate request branch, event generation and split. This is API authorization,
not OS authentication: clientInfo is self-reported, and an unrestricted same-user agent can
invoke the human CLI outside MCP. Keep approval commands under human control in that client.

Brain mode disables model requests at Client. Deterministic scope checks always apply; semantic
Navigator scope classification is explicitly skipped. Both script sources share execution guards.
Test data is exposed per attempt only, and plaintext is removed before repair waiting.

MCP returns indexed, hash-checked evidence and bounded summaries; it omits raw inventories and
run stdout/stderr. Parquet metadata is checked before reading oversized tables. Content checks
cannot prove that a generated plot/table never encodes an individual row. See [MCP privacy](mcp.md).
