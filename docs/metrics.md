# Evaluation metrics

MLCA computes metrics from verified event records and request envelopes. It makes no model calls.
Run this before sharing evidence:

```sh
mlca -p STUDY metrics --json
mlca -p STUDY metrics --branch main --out metrics-copy.json
```

Both commands write `reports/generated/metrics.json`; `--out` writes a second copy. Neither mutates
the event log. Branch metrics include ancestor evidence and requests linked to that branch's steps
or sessions. They are not a subtraction of work done before the branch.

## Sources

Each numeric measurement is `{value, source}`. Sources are `exact` (recorded), `derived` (counts,
time differences or estimates), `client-reported` (external-client usage), or `unavailable` (null).
Zero means an observed zero, never missing usage. A total becomes unavailable if any contributing
value is missing. Sample statistics list available and unavailable counts; SD needs two values.

## Fields

| Section | Meaning and limits |
|---|---|
| `run` | Snapshot references, modes/principals, start/end, wall duration, branch, events and completion. Completion requires report reached and recorded checks passed. Snapshots contain MLCA/checkout/Python/OS/kernel/CPU/core/RAM/NVIDIA inventory, uv/bubblewrap, template/environment hashes and role provider/model/settings. Missing hardware is unavailable; a sandbox capability snapshot is not a successful execution. Actual sandbox levels are in run records. |
| `steps` | Action/event, distinct submitted script attempts, first-try success, recovered flag, final status and run duration. Provider retries are model calls, not additional submitted scripts. |
| `recovery` | Steps with failed attempts; success after failure without a human decision is automatic. Success with a human action between failure and completion is after-human. Policy and external-agent actions are not human actions. Unrecovered attempts remain in the report. |
| `failures` | Recorded root failures/refusals by category. Terminal StepFailed/API wrappers of the same session/event/category are suppressed; this is not a count of unique research tasks. Historical missing categories are not inferred from text. |
| `interventions` | Option/custom decisions, words, confirmations, requested/granted/declined approvals, unlocks, packages and edits, grouped by principal. `user` is human; `user:policy/<hash>` is scripted policy; `agent:<client>/<version>` is external automation. Script edit line counts compare frozen code to its edited view; non-script edits stay unavailable. |
| `time` | LLM request latency, compute duration, human waits/activity, agent decision waits and approximate residual overhead. Waits are upper bounds: tabs or terminals can remain unattended and intervals can overlap. Negative residuals are retained, not clamped into misleading positive time. |
| `models` | Calls, input/output/cache tokens and cost by role, configured models, actual returned `model_reported`, cost sources. `request_settings` are the temperature/max output tokens sent. Failed or unmetered calls retain null usage. Estimated pricing is derived, not provider billing. Brain-mode external usage is unavailable until imported. |
| `egress` | Request/tool-result counts, serialized bytes and declared content categories. `sample_rows_sent` describes declared categories only: it cannot detect arbitrary encoding or a provider's inference from a plot. Imported usage causes no model egress. |
| `provenance` | Metrics/tables/figures with an intact artifact → completed step → hashed script → run chain. Coverage is unavailable if no such items exist. This checks recorded integrity, not numerical correctness. |
| `results` | Recorded primary validation/test value and CI (ROC AUC or C-index), and selected-model fact when present. Missing values remain unavailable. |
| `safeguards` | Categorized refusal records and step references. |
| `decisions` | Ordered event/action/parameter hash/principal; custom text is hashed, never reproduced here. |

The fixed failure taxonomy is: `static_check`, `sandbox_denied`, `runtime_error:<ExceptionType>`,
`timeout`, `missing_output`, `fit_rule`, `test_lock`, `scope_layer1`, `scope_layer2`, `gate_blocked`,
`invalid_options`, `provider_error`, `budget_stop`, `privacy_refusal`, `abandoned`. Categories are
assigned at the failure boundary. Unknown application failures retain their exception type.

### TUI active time

For a pending decision, keyboard/mouse activity samples monotonic time. Intervals at most 120 s
count; an entire longer gap is excluded. `idle_cutoff_s` accompanies the value. This is an activity
estimate, not a measurement of attention or thinking time. CLI/MCP activity is unavailable. Proposal
wait starts at the matching OptionsProposed; approval wait starts at ApprovalRequested; a direct
confirmation waits from the first record showing it is the sole outstanding check.

## Import brain-mode client usage

After disconnecting the client (so the run has an end timestamp), import its local session:

```sh
mlca -p STUDY usage import --client claude --session /path/to/session.jsonl
mlca -p STUDY usage import --client codex --session SESSION_ID
mlca -p STUDY usage import --client claude --session /path/to/session.jsonl --from 2026-10-07T10:00:00Z --to 2026-10-07T11:00:00Z
mlca -p STUDY metrics --json
```

Only message/request identifiers, model, timestamps and numeric usage fields persist. No message,
reasoning, command, source path or tool output is copied. Imports are idempotent and scoped to the
recorded brain-session window; optional bounds narrow it further. Do not reuse one external agent
session for simultaneous studies: the import cannot infer which study caused a token charge.
Missing costs remain null; a subscription is not a claim of zero inference cost.

- Claude Code (author's inspected 2.1.292 shape): assistant JSONL has `message.id`, `message.model`,
  `message.usage` with input/output, cache-read and cache-creation fields. Repeated message IDs update
  the same envelope rather than adding charges. Locations: `~/.claude/projects/*/*.jsonl`.
- Codex CLI **0.160.1**, locally checked via usage-field names only: `session_meta` identifies the
  session; `turn_context` supplies model; `event_msg` / `token_count` has
  `info.total_token_usage` and `info.last_token_usage`. Cumulative differences avoid repeated-counter
  double-counting. Fields include input/output/cached-input/cache-write/reasoning-output tokens.
  The first event uses its reported last usage; if absent it remains unknown. Locations:
  `~/.codex/sessions/**/*.jsonl`. This is a tested version-specific adapter, not a stable API promise.
  [Official Codex CLI documentation](https://learn.chatgpt.com/docs/codex/cli) describes the client;
  the private rollout shape was checked locally, rather than inferred from public documentation.

## Independent benchmark runs

```sh
mlca bench run docs/task-cards/example.yaml --runs 3 --out /path/to/fresh-bench --mode driver --seed 42
mlca bench summarize /path/to/fresh-bench
```

Edit the task card first. Data/brief, template, option policy, custom instructions, confirmations,
unlock consent, packages, budgets and maximum turns are explicit. Policy choices/approvals use
`user:policy/<task-card-sha12>` and the full card hash appears in every run snapshot. Ordinary MCP
agents cannot invoke this trusted headless policy capability or supply this principal.

`default_first` chooses the catalog default; `navigator_first` takes the Navigator's first valid
primary action; `seeded_random` chooses a primary action with seeded randomness. The split seed is
fixed by `--seed` across runs; option RNG uses seed plus run index. MLCA does not claim to seed
external provider inference. Each run has a fresh environment/log/provider calls. Request bounds
reserve conservative cost; total-budget exhaustion is retained as a failed run. Runs are sequential.

`bench_summary.json` has completion rate, categorized failures, steps, first-try/recovery rates,
principal-separated interventions, time, usage/cost and final-metric mean/sample SD/min/max.
It includes failures in the run list and completion denominator. Numeric means use available values
and label missing counts. A recovery rate without any failed steps is undefined. Decision consistency
reports the dominant complete sequence share, per-event action-sequence share, and pairwise aligned
(event, action, parameter hash) agreement. Intentional seed/policy changes can change agreement.
`bench_summary.md` provides a readable run list linked to the detailed numbers.

`replay --verify` reruns frozen scripts to check reproducibility; **bench** makes independent agent
runs with fresh calls. Synthetic/fake-provider checks measure harness behavior, not scientific
performance. Real-data studies, AutoML/plain-LLM baselines and planted-flaw tasks belong in the
paper's experiment workspace and are not implemented or run by this instrumentation phase.
