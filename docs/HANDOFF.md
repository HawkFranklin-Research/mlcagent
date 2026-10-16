## Work order 05 — batch-01 reviewed; batch-02 regression gate passed (16 October 2026)

Batch-01 ended on unchanged code 6827d09, controller eb70bd3, rails-0.3 and
DeepSeek V4.1 Flash: **0/12 completed**, 173 requests, 378,074 input / 714,702
output tokens, reasoning 664,452 included in output, provider-reported cost
**$0.742783848**. No unknown core usage fields or provider failures. Experiments
commit d792b50 preserves curated evidence and every failed/interrupted outcome.
Covertype was stopped early by the implementing agent for an engine collector
bottleneck after a successful 1.918 s sandbox audit. It is an infrastructure
intervention/protocol deviation, not a model failure or measured timeout.

Between-batch corrections:
- c2b9978 / B-0011–B-0013: explicit setup wire fields with historical decoding
  preserved; streaming same-verdict privacy matching; actionable, value-free
  metric/library diagnostic hints. Focused regressions: 22 passed.
- e433c51 / L-0003: rails-0.4, 25 instruction rails; importable saved objects,
  one-time named-column frontends, compatible output APIs and numeric-only
  correlation screens. Focused rails/genericity/repair regressions: 18 passed.
- The complete native gate passed: **416 passed, 1 skipped**, zero failures
  or errors, across all 95 test files in four isolated offline processes
  (slowest partition 521.40 s). Logs/XML and four zero exit codes:
  /home/prime/.cache/mlca-batch02-parallel-gate/. Experiments: 18 passed.
  No live batch-02 call occurred before this gate passed.

Exact next step: launch scripts/run_batch.py --batch 2
--out bench/dev-loop/batch-02 --model deepseek/deepseek-v4.1-flash --concurrency 6
from the experiments repository. All twelve prior studies failed; use fresh
projects. Keep generation settings unchanged in this engine/rails batch. Never
change source during active jobs. Current controllers are stopped; consult
batch.json before assuming an earlier process is still alive.

One scientific question is pending: Retail's static customer segmentation versus
the manifest's CustomerID/InvoiceDate temporal requirement. The author was asked;
researcher expectations stay unchanged meanwhile. They never enter agent input.
Thirteen batch-01 request errors exhausted the 16,384-token output budget, many
entirely on reasoning. Official metadata observed during that batch advertises
high as default and low as supported. Any effort change must be explicit and
recorded at a later separate batch boundary; none has been made yet.

Finished-batch large private fingerprint caches are losslessly archived with
SHA-256 verification; raw sources, logs, scripts, model outputs and vaults remain.
See experiments batch-01/private-cache-archives.json for restoration instructions;
restore original cache bytes before opening an archived project for privacy reads.
Original archives stay private/untracked. The author also freed disk space.

O1–O7 built, with offline coverage; live acceptance not established. O8: batch
loop active, consolidated repairs and full regression gate passed. O9 freeze not started.
Acceptance K=3, then ablation, or ten-batch/five-day cap, then Part C. No held-out
access, biomedical run, paper edit, push, upload, release, tag or version bump.
Automatic CLI OpenRouter onboarding remains a later item. Paid DeepSeek calls
are authorized without a spending ceiling; never print or persist credentials.

---

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

# Handoff — 15 October 2026: organized plan

**Read `plan.md`, section "Organized plan (15 October 2026)", first.** MLCA is now developed as an autonomous agent with rails: `mlca run <path>`, a halt window for the human, an explicit rails layer with a ledger of the failures that caused each rail, and templates for more problem types. Rails are developed on about 10 public tables, frozen, then checked on 2–3 held-out tables and evaluated on the biomedical studies. Unfinished P17/P18 items and `plan_mcp.md` MB6/M7 are stopped. `master` is at `ad92ebd` (327 passed, 1 skipped). No completed live run. Open decisions are listed in the plan; the first is the list of development and held-out tables. No push, publication, upload or live call without the author's go-ahead.

---

# Work order status — 14 October 2026 (historical)

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
