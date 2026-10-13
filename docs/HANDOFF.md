# Handoff — revision cut P16/P14.6, 13 October 2026

Current work is P16 accounting plus template-option recovery after Navigator failure. Worker code
remains the measured path; failed Worker steps are never replaced by reference scripts. Level A
and explicit level-B opt-in remain unchanged. Read plan.md's Answers to the implementing agent and
docs/P16_ACCOUNTING.md. Live calls are deferred. Reconcile waits for the actual Activity CSV in the
paper's experiments/10_agent_metrics/openrouter_activity folder. Most P14 and all P15 wait for freeze.
Full offline working-tree suite: **245 passed, 1 skipped in 678.51 s** (PowerShell unavailable). Ruff lint and formatting pass. The isolated selective P16/P14.6 candidate passed 34 tests, independently of the other uncommitted work.
Local phase commits: 8472fb4 (P16), cb00eec (P14.6).
Pre-existing uncommitted P13, catalogue snapshots and browser plans remain preserved and unmerged.
There is no configured remote; do not publish, push, tag, bump versions or use computer controls.

## Earlier handoff (historical)

# Handoff — MX alignment complete, 13 October 2026

MX1–MX6 implemented in ordered local commits. Full offline suite: **202 passed, 1 skipped in 719.16 s** (PowerShell unavailable). Ruff lint/format pass. Installed source refreshed after MX5; final refresh includes MX6. No live model calls, computer controls, remote pushes or beta 3 publication. Public beta 2 is unchanged; local development source still reports 0.2.0b2. Master and browser plans remain untouched.

Work is on native-onboarding. Read plan_mcp.md section 13, docs/mcp.md, docs/m7-vm-brain-mode.md and docs/metrics.md. M7 should use the current source checkout: the published beta lacks MX changes. Progress notifications are request-scoped/client-dependent; polling is guaranteed. Client-presence files are presentation hints, never authorization. Study-field/environment changes still require idle work; confirmations can be approved while scripts are awaited.

Next: author-run M7 with real clients/data, separately authorized live inference. Do not publish 0.2.0b3 until requested. Untracked plan_web.md and plan_web_mcp.md are preserved and unimplemented.

## Historical initial handoff (superseded)

# Handoff — 6 October 2026

The coding request authorized the complete P0–P8 source implementation and local phase commits.
The user explicitly deferred tests, smoke/full-cycle runs and live model calls. The anemia dataset is
on another machine and will be provided later. Test sources/fixtures were also deferred; do not claim
acceptance-check completion.

Read README.md, IMPLEMENTATION_STATUS.md, DECISIONS.md and security-model.md before continuing.
The original plan.md is preserved. No reference code was copied. License and image-logo choices are
pending. Both workflow templates are DRAFT and need author scientific review.

Key locations: src/mlca/api.py (front-end contract), log/ (durable records and pure state), engine/
(gates/options/scope/facts/turns/split), runner/ and sandbox/ (execution, reproduction and test access),
llm/ (providers/request evidence), project/ (init/env/views), report/, tui/, src/mlca_runtime/.

Static lint/format checks pass. The tool environment is .venv, dependencies are locked with uv.lock.
No model/provider is configured automatically. Package installation is complete; no CLI launch was used
as a smoke check. No remote or publication has been configured. The paper and legacy/reference folders
were not edited.

When validation is authorized, begin with offline invariant/contract tests and synthetic data, then
CLI/Textual smoke runs, bubblewrap mount checks and a fake-provider complete cycle. Inspect unsupported
host namespaces, library import/audit interactions and report reproducibility before scientific runs.
Then obtain the anemia dataset and exact model/provider settings for explicit live studies.
P9 still needs separate authorization.
