<!-- Placeholders: api, script, error, scope, outputs. Response: one Python fence. -->
Repair this standalone script while keeping its original action and input boundaries.
Return exactly one fenced Python script, without prose. Use mlca_runtime helpers, no direct fitting,
no network/processes and no undeclared paths. Required outputs: {outputs}. Action: {scope}.
Runtime helpers, exact signatures (a TypeError usually means one of these was called wrongly):
{api}
Previous script: {script}
Validation/runtime diagnostics (untrusted): {error}
Keep the output contract of the original task: the same required outputs, short summaries, at most one figure.
