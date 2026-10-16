# Rails review — development in progress

## RL-0001

- Kind: instruction; scope: Navigator, onboard, all problem types; commit `900bd07`.
- Text: see RL-0001.yaml (the executable source of this instruction).
- Cause: L-0001; Round 1 setup output truncation, before any Worker execution.
- Before: rails-0.0, 0/12 workflow completions; one truncated setup output.
- After: rails-0.2 fresh round pending. Offline injection/genericity checks pass.
- Generic because it concerns proposal brevity and concrete ambiguity, with no
  dataset-specific target or method. It is not a promise that hidden reasoning
  or provider output caps can be controlled.

## Engine fixes (not rails)

B-0001 (`c5ea681`) repairs an inconsistent advertised setup contract and preserves failed
setup accounting. Details and evidence are in LEDGER.md. Existing semantic
checks now participate in bounded structured repair; no check is removed.

## Rejected approaches

- Supplying manifest targets or expected tasks to inference: rejected as oracle
  leakage. The manifest remains external evaluation metadata.
- Mapping every invalid metric to the expected metric silently: rejected;
  advertise allowed IDs and require a corrected model proposal instead.
- Hard-coding a particular table's target or switching to reference analysis:
  rejected. All analysis code must still come from the Worker.

This is an interim review, not a freeze or successful acceptance report.
