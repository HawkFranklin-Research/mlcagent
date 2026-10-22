# Reopening-v2: RL-0029 / rails-0.15 — 23 October 2026

Implemented the author-approved Step 4 batch-01 interpretation follow-up only.
RL-0029 bounds non-survival interpretation above 500 input features to native
importances or the top 50 ranked features with at most 5 permutation repeats.
The classification work order now makes its 20-repeat budget conditional on
at most 500 features, including in the Navigator's action view. Full prediction
input schemas and the existing 300-second step limit remain unchanged.

Evidence paths and instruction limits: rails/LEDGER.md L-0014. Offline checks:
36 rail/genericity/prompt/repair/snapshot/wide-context tests plus 12 template and
runtime-contract tests passed (48 total); Ruff and whitespace checks pass. The
full suite was not rerun. No live model calls or batches, data-table inspection,
held-out/biomedical access, freeze, push, upload or installed-CLI refresh.
Existing untracked files were preserved. This request stops after the local commit;
the testing agent's prospective batch-02 is specified in the experiments work order.

---

# Reopening-v2 offline fixes — 22 October 2026

Read `../mlcagent-experiments/docs/work-orders/reopening-v2-readiness.md` and the
reopening-v2 work order. Steps 1–3 are complete: E-W1 63597cf, E-W2 65232e5,
E-M1 f7e14b0, E-S1 e7bb53f, rails-0.14 7e3a635. All commits are local on master.
Full source suite at 7e3a635: **536 passed, 1 skipped in 1291.95 seconds**.
Experiments-controller suite: **125 passed in 21.02 seconds**. Ruff and changed-file
formatting pass. Three new table checksums/dimensions verified; already committed
in 1c21032. The interrupted schema_summary.py is integrated and regression-tested.

No development batch, freeze-v2, eval-02, live model call, push, upload, installed
CLI refresh or paper edit was performed. DEEPSEEK_API_KEY is absent from this
session; never replace the environment-only rule with a credential-file read.
Disk was about 54 GiB free at inspection. Recheck launch gates. The testing agent
runs/reports only; engine/rail changes return to the coding agent. Resume Step 4
on all 15 development tables once its environment is ready. Preserve eval-01,
existing untracked files and the original freeze-v1 tag. No survival rail added.

---

## Work order 05 — Phase 1 development loop complete (all 12 tables qualified, rails-0.9)

Series 12/12 development tables have now qualified with complete end-to-end runs,
exact setup agreement, and verified zero leakage:
- Batch 02: Heart Disease, Abalone, Energy Efficiency qualified.
- Batch 03: Breast Cancer, Adult, Dry Bean, Covertype (full 581,012 rows) qualified.
- Batch 04: Anuran Calls, Seeds qualified.
- Batch 05: Bike Sharing (hourly) qualified.
- Batch 07: Optical Digits qualified (representation learning, 2D bottleneck array).
- Batch 08: Online Retail qualified (static customer clustering, RFM aggregation, empty time columns).

Total development accounting across all 8 batches:
- Requests: 1,265
- Input tokens: 3,001,991; Output tokens: 4,820,251; Reasoning tokens: 4,425,729
- Total known cost: $4.7985 USD
- Zero unknown request costs; model reported: DeepSeek V4.1 Flash (100%).

Key infrastructure and rails achievements:
- Compact private fingerprint cache v3 (B-0026): 8x–10x reduction on large caches,
  leaving >38 GB free disk space for acceptance testing.
- Rails version: rails-0.9 (26 instruction rails, zero hardcoded rules).
- All unit and contract tests passing (19 unit passed, 18 experiments passed).
- CLI binary updated and verified via `uv tool install --reinstall --editable .`.

Next exact step:
Step 5 Acceptance testing: Run all 12 development tables K = 3 times on this frozen
version (36 studies, same queue) using:
`python scripts/run_batch.py --out bench/dev-loop/acceptance --model deepseek/deepseek-v4.1-flash --reasoning-effort low --concurrency 6 --replicates 3`

---

## Work order05 — batch05 reviewed; batch06 final gate passed

Series10/12 tables have qualified at least once; K=3 acceptance/ablation have
not started. Batch04 on codeafe46c3/controller1344fc8/rails06/defaultreasoning:
Anuran and Seeds newly qualified; Bike and Retail completed but setup disagreed
(Bike also failed chronological leakage). Digits failed EDA truncation.
184requests,1203454tokens,$0.74417513. Batch05 changed ONLY requested effort
to low, with exact same source/rails/model/limits: Bike qualified, Digits failed
validation, Retail failed split after invalid Navigator metadata triggered the
wrong fallback.84requests,416642tokens,$0.2442439458. Cumulative sincebatch01:
1082requests,6813806tokens,$4.3661140112; core usage known. Raw provider
reasoning details have an observed per-request inconsistency, preserved, not
guessed or added again to completion. No randomized causal effect claimed.

Experiments evidence4a380e1/9447df6:1086/535 hashed text artifacts respectively,
127/52 omitted binary/table hashes, private data excluded, locks included.
Seeds external test-onlyARI.3387861089/NMI.4850069866 on42 test rows, with126
training assignments retained; NOT agent work and never used to tune rails.

Consolidated source aa66fac,rail3f76c3f/rails07:
- Joint group_time splitting preserves groups AND chronology by merging
 overlapping intervals/ties into components, using near-requested row fractions,
 or refusing impossible three-way constraints. No rows dropped, no random
 fallback. Existing single-constraint paths preserved.
- Navigator sees bare local goal IDs, exact parameter schemas/action contracts
 and supported question-effect examples. Invalid mutation effects remain
 refused; essential unsupported decisions pause for the human. Retail05 BOTH
 model replies recommended preparation; fallback chose distributions only
 after goal/question metadata failed. Do not misattribute it to the model
 ignoring preparation or to presentation word counts.
- Representation validation requests metrics only; explicit PCA vs MLP final
 decoder interfaces and fixed value-free diagnostics. Digits05 computed its
 metrics after repairs but crashed saving an UNDECLARED validation embedding
 without explicit row_id/partition. Runtime guards unchanged. RL0022 refined;
 still26 instruction rails, no new checks/defaults.

Final full offline gate:476passed,1skipped,100files,zero failures/errors; four
exitcodes0,slowest323.54s. Logs/XML ~/.cache/mlca-batch06-final-gate/.
Previous complete gate467passed1skip. Focused28passed57.68s including guided
and training-review integration;latest16 focused passed1.66s. Experiments
18passed12.38s. Ruff passes; no real-data reference analysis or live tests.

Next: launch fresh batch06 ONLYoptical_digits,online_retail; fixed DeepSeek
V4.1Flash,LOW effort,temp0,max16384,concurrency6,shared60rpm,one large atonce,
A only,300s call/script,5400s study,three Worker attempts. Check live PID/log
~/.cache/mlca-05-batch-controller.json; never edit source during active jobs.
Author question about future compatible extra constraints remains pending.
Current strict metadata scores and previous outcomes are unchanged. Bike
chronology stays mandatory; Retail static segmentation is approved prospectively.

Disk~39GiB; old closed derived caches losslessly archived, restore before old
project Session/privacy reads. Covertype's45GB raw cache will need capacity or
generic compaction before full36-study acceptance. Compaction is proposed only,
NOT implemented; no primary data/model/log/vault removed.
O1–O7 built,O8continues,O9freezeNOTstarted. Noheldout,biomedical,paper edits,
push,remote,upload,tag,version bump or publication. CLI automatic sign-in deferred.

---

## Work order 05 — batch03 reviewed; batch04 launch gate passed

Batch03: four new qualifying completions (Breast Cancer, Adult, Dry Bean,
full-size Covertype), seven of twelve qualified at least once. Acceptance
K=3 and ablation remain pending.279 requests;663898 input+1152202 output
(reasoning1076403 INCLUDED);$1.1659709834. Cumulative since batch01:
814 requests,5193710 total tokens,$3.3776949354,all core usage known.
Curated evidence/review:experiments53dad9c,1730 verified text artifact hashes.

Local engine9295c30 and compatibility/guided follow-ups e40248d,6aba218:
exact read-only /proc/self/maps with real sandbox KMeans+denial test; all
six scoring templates use the nested declared metric; bounded scoring-only
retry stays at validation in both guided-driver and CLI paths. Native unguided
sessions receive the same protocol snapshot. No fit/test/privacy rule relaxed.
Rails e4c8371,rails06,L0005: existing temporal,per-target categorical metric
and PCA reconstruction instructions strengthened. No dataset-specific rail.
Optional reasoning effort transport/accounting is implemented but unset for
batch04. Experiments1344fc8 records it and guards ablation-setting identity.

Final full offline gate:467 passed,1 skipped,98 files,zero failures/errors;
four exit codes0,slowest438.59s. Logs/XML ~/.cache/mlca-batch04-complete-gate/.
Earlier partial gates are superseded; their logs are retained, not passing
gates. Final focused62 passed44.94s; native compatibility fixture group29
passed134.06s. Experiments tests/:18 passed12.78s. Ruff passes; changed-file
format and whitespace checks pass. The unrelated existing scope_guard test
has a whole-tree format discrepancy and was preserved.

Author decision: future Retail runs evaluate static customer segmentation,
recency relative to the last transaction date. No chronological requirement;
grouping/identifier exclusions unchanged. Earlier scores retained. Bike keeps
its chronological requirement. Manifest remains researcher-only.

Next launch: python ~/.cache/mlca-launch-batch04.py (asserts gate and clean
source). Five failed/deferred tables only:anuran_calls,bike_sharing_hourly,
seeds,optical_digits,online_retail. DeepSeek V4.1 Flash,temp0,max16384,
provider-default reasoning;6 parallel,shared60rpm,one large atonce,A only,
5400s study/300s call+script,3 Worker attempts. Consult
~/.cache/mlca-05-batch-controller.json for live PID/log/source identities;
never edit source during active jobs. Batch05 changes only requested reasoning
effort to low (supported efforts max/high/low/none,not medium); same engine,
rails,model and other settings. No current claim about that setting's effect.

O1–O7 built;O8 development loop continues;O9 freeze NOT started. No held-out
access,biomedical run,paper edit,push,remote,upload,version bump or publication.
No no-AI real-data reference run. Automatic CLI OpenRouter sign-in deferred.
Storage compaction remains proposed,not implemented; check disk before large
acceptance repeats. Closed derived caches may be byte-verified archived only
after worker exit/scoring; restore original caches before reopening old projects.

---

## Work order 05 — batch 03 closed, batch 04 gate running

Batch03 verified: four new qualifying completions (Breast, Adult, Dry Bean,
Covertype); seven of twelve have qualified at least once. 279 requests,663898
input+1152202 output (1076403 reasoning included),$1.1659709834. Cumulative
814 requests,5193710 tokens,$3.3776949354. Acceptance/ablation not started.
Experiments evidence53dad9c: REVIEW plus1730 hashed curated text artifacts,
180 omitted binary/table hashes; source artifacts retained.

Author approved prospective static customer segmentation for Retail. Manifest
removes its time requirement; grouping/identifier exclusion remain. Older scores
unchanged. Bike retains chronology. Next batch includes five remaining tables.

Engine9295c30: exact read-only /proc/self/maps; universal nested declared metric
in12 scoring actions; bounded validation-only missing-metric retry; optional
recorded reasoning effort (unset in batch04). Rails e4c8371/rails06: revised
RL0004 temporal rows,RL0018 categorical per-output metrics,RL0022 PCA inverse
transform. Compatibility e40248d supplies protocol to unguided native sessions.
Experiments1344fc8 records effort and guards ablation setting identity.
Focused gates44/78 passed; complete legacy/native fixture group29 passed in134s.
Full gate currently running in ~/.cache/mlca-batch04-corrected-gate,98files.
The first partial gate was intentionally interrupted before native correction.
Partition4 assertion expected only the data file; it is updated to expect
protocol metadata too, with external data still sealed. Partition4 is rerun
against unchanged runtime source; keep superseded logs and interpreter-start
error separate, not counted as tests. Three other partitions continue.
No live request before all four final partitions pass.

After gate: commit test/status updates and ensure both tracked trees clean.
Launch batch04 fresh on anuran_calls,bike_sharing_hourly,seeds,optical_digits,
online_retail,DeepSeek V4.1 Flash,default reasoning unchanged,temp0,max16384,
concurrency6,rpm60,one large table at once,5400s study/300s call+script,A only.
Record PID in ~/.cache/mlca-05-batch-controller.json; no source edits while active.
Batch05 is setting-only low effort: official cached metadata supports max/high/
low/none,not medium; code/rails/model/settings otherwise unchanged. Scorer
criteria are researcher-only; no hidden labels/manifest fed to agent.
Compact private fingerprint storage remains a proposed future improvement,
not implemented or claimed. Check disk before repeated full-size acceptance;
restore archived caches before Session/privacy reads on prior projects.
No held-out access, biomedical run,paper edit,push,freeze,tag or publication.
CLI automatic OpenRouter sign-in deferred. Continue acceptanceK3/ablation/cap
then PartC as work order05 specifies; no no-AI real-data reference runs.

---

## Work order05 — batch02 reviewed; batch03 full gate (16 October2026)

Batch02 finished:3/12 qualifying completions (Heart, Abalone, Energy Efficiency),
9 retained failures. Frozen code2f04c0b/controller0f8bc4c/rails04, unchanged
DeepSeek V4.1 Flash. Eleven setups agree; Retail static segmentation omits the
manifest time column. Clean partial fit/split checks are not study completion.
362 requests;793836 input+1490998 output (1369764 reasoning INCLUDED),
$1.468940104; cumulative535 requests/3377610 total tokens/$2.211723952.
All usage known;25 output-truncated requests, no outage/rate-limit failures.
Evidence:experiments4a9a60d,2278 hashed text artifacts,12 environment lockfiles,
215 omitted binary/table hashes. Raw attempts preserved. No unsupervised
completion, so no external hidden-label score.

Consolidated local commits:
- 43b7407/B0014–16: Parquet prediction-audit contracts, explicit row_id/partition
  API, binary/multiclass primary metrics and value-free scoring hints.40 focused
  new/legacy regressions passed in1.70s.
- 6b0549b/L0004:rails05,26 instruction rails. Align target/probability types,
  select existing entity preparation before distribution-only EDA completes,
  persist feature derivations.34 focused tests/genericity passed in2.49s.
- 5e1dcfc/B0017:explicit frozen row-partition contracts; audits validate val-only
  or test-only, while legacy and unsupervised test data retain train+test.
 42 focused runtime/collector/metric/rail regressions passed in2.97s.
No guard weakened, reference script, model or generation setting changed.

Full consolidated offline gate PASSED:445 passed,1 skipped, zero failures/errors
(all97 test files; slowest partition475.42s). Logs/XML:
/home/prime/.cache/mlca-batch03-final-gate/ (four logs/XML,exit-codes.json).
All four exit codes are0; XML totals446 tests including the single skip.
The earlier gate was explicitly interrupted before the population-contract
correction; its logs remain in mlca-batch03-parallel-gate/ as superseded.
Previous native gate416passed1skip. Experiments tests/:18 passed in11.41s against the final source. Never
run pytest at experiments root because raw analysis scripts are not test files.
No live batch03 call before all gate results pass.

Next:ensure both tracked trees clean, then launch from experiments:
../mlca-revized/.venv/bin/python scripts/run_batch.py --batch 3
--out bench/dev-loop/batch-03 --model deepseek/deepseek-v4.1-flash --concurrency 6
--tables breast_cancer_diagnostic adult dry_bean covertype anuran_calls
bike_sharing_hourly seeds optical_digits
This eight-table list defers Retail pending author choice of temporal versus
static segmentation. A refreshed async question is pending. If answered first,
record a prospective criterion revision without rewriting old scores, and
include Retail as appropriate. Never inject manifest answers into the agent.
Generation remains temp0/max16384/provider-default reasoning for this engine/
rails batch. Any effort change belongs at a separate recorded boundary.

Covertype completed full registration/splitting/both fits without implementer
interruption, then exposed the metric action conflict. Its45GB private cache
was losslessly archived3.5GB after exit/scoring and round-trip SHA256 checking.
Seven closed caches archived; batch02/private-cache-archives.json gives restore
instructions. Restore original cache before reopening archived projects through Session or performing privacy reads.
No data, model, output, script, log or vault removed.326 dead-PID offline pytest
scratch folders cleaned (~4GiB); gate logs/XML retained. Free disk~44GiB. Large closed-cache archival may use private RAM scratch,
with uncompressed SHA verification before reclaiming the redundant cache and
verified/fsynced durable archive copy before removing scratch. Primary artifacts
remain intact; record staging/restoration metadata separately.
No study paused/interrupted/rerun for storage. These are infrastructure records.

O1–O7 built;O8 loop continues;O9freeze NOT started. AcceptanceK3/ablation
pending;cap10batches/5days. No held-out access, biomedical run, paper edit,
push/remote/upload/release/tag/package bump. CLI automatic OpenRouter onboarding
remains deferred. Paid calls authorized; never print credentials. Update this
checkpoint before any usage-limit stop.

---

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
