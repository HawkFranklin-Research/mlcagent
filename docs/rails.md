# Workflow rails

Rails are fixed, generic instructions, checks or defaults. Existing engine rules
remain authoritative; a rail never grants access or relaxes a scientific check.
The baseline is `rails-0.0`, with no extracted instruction files.

Each `rails/RL-NNNN.yaml` has id, kind, roles, events, problem_types, reason,
ledger and added_in. Instructions also have text. Engine checks/defaults specify
a trusted registered check function and point (`before_step` or `after_step`).
Unknown fields, scopes, duplicate IDs and unregistered functions are rejected.
Instructions are appended in ID order under “Fixed workflow rails”.

At initialization, VERSION and rail YAML are copied into `.mlca/rails`.
The version and content digest are anchored in ProjectCreated and RunSnapshot;
opening a changed snapshot fails. Historical projects use their unchanged baseline.
RailFired records attribute engine check/default firings to the exact rail.

`rails/LEDGER.md` links additions to failure evidence and local commits. Rail text
and reasons must not contain development dataset IDs, filenames or column names.
A regression test checks those constraints without opening held-out files.
