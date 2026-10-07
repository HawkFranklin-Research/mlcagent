# MLCA: Machine Learning Copilot Agent (v2)

MLCA guides a machine-learning study step by step. Instead of an open-ended chat, a study moves through a fixed sequence of **events**. At each step you choose from a few natural **options**, or give a custom instruction limited to the current event. Every step becomes a standalone, numbered script with recorded outputs. Rules that protect the science are enforced by code, not by prompts: the test set stays locked, models are fitted on training rows only, and every number has a source.

```
onboard → data → eda → split 🔒 → preprocess → features → model ⇄ validate → test (unlock once) → interpret → report
                                     └──────── iteration loop (validation only) ────────┘
```

## How a step works

1. **Status:** the engine rebuilds the project state from its event log.
2. **Options:** two to three options from the current event's action catalog, plus `custom`. When an event is done, the next event is offered.
3. **Choice:** you choose (or an agent chooses; see *Two ways to use MLCA*).
4. **Script:** a short, standalone Python script is written for the action and run in a sandbox:
   - only declared inputs are readable;
   - no network;
   - the test set is invisible until unlocked.
5. **Record:** outputs, metrics and facts (each citing the file it came from) go into the event log. The event's sub-goals are then checked by code.

Each event has a goal, sub-goals, an action catalog and a custom-instruction scope. These are defined in a **workflow template**:
- `templates/tabular_classification/`: logistic baseline vs gradient boosting, ROC AUC;
- `templates/survival/`: Cox vs penalised Cox, C-index.

The template content is short by design; see [templates](docs/templates.md).

## Two ways to use MLCA

| | **Standalone** (available now) | **Docked to another agent through MCP** (available now) |
|---|---|---|
| Interface | terminal UI (`mlca`), CLI, browser view of the TUI (`mlca web`) | Claude Code, Codex, Hermes, OpenClaw, Cursor or any MCP client, connected with `mlca mcp` |
| Who proposes options and writes scripts | MLCA's own **Navigator** and **Worker** models (your API keys: OpenAI, OpenRouter or a local OpenAI-compatible server) | **Brain mode** (default): the connected agent proposes options and writes each script; MLCA makes no model calls. **Driver mode**: the agent only chooses; MLCA's Navigator and Worker do the work |
| Rules | all engine rules | the same engine rules; the agent cannot confirm sub-goals, unlock the test set or approve packages; it can only request them, and you approve in MLCA |
| Attribution | decisions recorded as `user` | decisions recorded as `agent:<client>/<version>`, so reports separate human and agent work |

In brain mode, a script written by Claude or Codex goes through exactly the same checks as one written by MLCA's Worker:
- option validation;
- static checks;
- the sandbox;
- the training-only fit rule;
- the test lock.

## Connect an agent

```sh
mlca mcp install --client claude --with-skill       # preview
mlca mcp install --client claude --with-skill --yes # register only with explicit consent
mlca mcp install --client codex                    # preview
mlca mcp doctor                                   # real stdio tool discovery
```

The server is included in the Python package. See [MCP docking](docs/mcp.md) for Hermes,
OpenClaw, Cursor, work orders, polling, privacy and approval commands. Human-only enforcement
is a Session/MCP boundary; MCP client identity is attribution, not OS authentication.

## Install

Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/) are required. Install the beta with an explicit version:

```sh
uv tool install mlca==0.2.0b1
```

Plain `uv tool install mlca` does not select this prerelease. Shell download, npm and Homebrew channels remain unpublished.

From this checkout: `uv sync --group dev`, then `uv run mlca`. See [installation](docs/install.md).

**Isolation:**
- **Linux:** full isolation (level A) with bubblewrap: `sudo apt install bubblewrap`.
- **macOS and native Windows:** only the weaker level B, which must be enabled explicitly (`sandbox.allow_level_b: true`).
- **Windows:** WSL2 is recommended.

## Configure models (standalone mode)

Copy [examples/config.yaml](examples/config.yaml) to `~/.config/mlca/config.yaml` (or run `mlca config edit`). Choose a provider and model for each role. Keys are read from environment variables (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`) and never written to disk. No default models or prices are assumed. See [providers](docs/providers.md).

## Quick start

```bash
mlca init ./study --data data.csv --template tabular_classification   # asks the brief; resolves the target column
mlca -p ./study                                                        # terminal UI
# or step by step from the CLI:
mlca -p ./study options
mlca -p ./study choose 1
mlca -p ./study confirm brief_confirmed "Aim, target and unit checked"
mlca -p ./study next
```

**Human decisions are explicit:**
- `confirm <sub-goal> "<note>"` for author checks;
- `unlock-test --phrase "UNLOCK TEST" --reason "..."` once, in the test event;
- `package` approvals.

After the test set is unlocked, fitting, validation loops and package changes are closed for the project.

Supporting inspections follow the main actions in fallback menus. Once an event is complete,
the menu offers `next` first, then unrun supporting actions and scoped custom instructions.
Those steps preserve completed checks. To try a primary alternative, branch before its step.

## Trust boundary

MLCA enforces decisions and data access only through its own API and sandboxed steps.
A connected agent's native file or shell tools can bypass MCP: they may read the original data,
`.mlca/data/splits/`, the test key under the MLCA user-data directory, or invoke human approval
commands. Generated `tables/`, `figures/`, `reports/` and `scripts/` are also local copies of evidence.
Reports therefore describe `agent_file_access` as **unknown (outside MLCA)**.

`mlca -p ./study mcp install --client claude --scope project` previews recommended permissions;
`--yes` backs up and merges them into `./study/.claude/settings.json`. The block denies native
shell execution and reads/edits of registered data, private state, keys and evidence copies.
Other clients receive equivalent guidance. These are client restrictions, not OS authentication:
disable other filesystem tools and bypass modes, or use a separate OS identity/container.
See [MCP trust boundary](docs/mcp.md#trust-boundary) before connecting a client.

With `allow_sample_rows: false`, private salted fingerprints check values across all columns,
regardless of their names, at six and four significant digits. The additional table heuristic flags
at least `min(3, n_columns)` distinct cell matches to one source row; exact shared-column checks
also remain. Full-row facts are checked without requiring matching column names. Matching outputs
are flagged in reports; genuine summaries normally remain readable, but coincidental matches may
be refused. Existing indexes upgrade from unchanged registered data without decrypting the test set.

This guard catches accidental and simple copies, not a deliberate agent. In brain mode the agent
writes the code and can encode data in strings, noise, figures or other derived outputs. Those
results are sent to the agent's provider by design. For confidential data, use standalone driver
mode with every model local and no external agent receiving outputs; the heuristic cannot guarantee
confidentiality for brain mode.

## Scientific guard rails

| Rule | Where it is enforced |
|---|---|
| Options are only actions from the current event's catalog, with validated parameters | `engine/options.py` |
| An event can be entered only when its gate passes; sub-goals are ticked only by code checks or your confirmation | `engine/gates.py`, `engine/checks.py` |
| Custom instructions must stay in the event's scope | `engine/scope_guard.py` |
| The split is done by the engine; the test partition is encrypted until unlocked | `engine/split.py`, `sandbox/vault.py` |
| Scripts run sandboxed: declared inputs only, no network, writes only to their own step folder | `runner/`, `sandbox/` |
| In preprocess, features and model, every fit goes through `mlca_runtime.fit_record` on the exact frozen training rows; other events may not fit at all | `runner/static_checks.py`, `mlca_runtime` |
| Every fact cites the file it came from | `engine/facts.py` |

**Limits:** level B (macOS, Windows) is an audit hook, not an operating-system boundary. Code checks cannot prove the meaning of every computation. Domain review of targets, units, preprocessing and interpretation remains yours. See [security model](docs/security-model.md).

## Evidence and reproducibility

Everything lives in the project's `.mlca/` folder:
- the append-only, hash-chained event log;
- the frozen template;
- the analysis environment and its lock file;
- the immutable step folders;
- the encrypted test partition;
- the usage and egress logs.

The `scripts/`, `figures/`, `tables/`, `reports/` and `PROJECT_LOG.md` folders are regenerated views; edits to them are detected.

```bash
mlca log --verify        # integrity of the event log
mlca replay --verify     # re-run every step script in a fresh environment and compare outputs
mlca report all          # methods draft, provenance, figure index, usage (no model calls)
mlca branch alt --from <record or step>   # try another path; mlca checkout main to return
```

## Status

- **Core (plan.md):** P0–P8 built; beta version `0.2.0b1`. **106 offline tests pass, 1 skipped** (PowerShell unavailable); see [validation](docs/IMPLEMENTATION_STATUS.md).
- **Not yet done:**
  - runs with real providers;
  - the study on real data;
  - native macOS and Windows checks.
- **MCP docking ([plan_mcp.md](plan_mcp.md)):** M0–M6 implemented: 14 stdio tools, brain/driver modes, human approvals, filtered evidence and usage records. Manual runs in real clients (M7) remain pending.
- **Licence:** [CC BY-NC-ND 4.0](LICENSE) (`CC-BY-NC-ND-4.0`), chosen by the author. The approved package name is `mlca`.

## Documentation

| Document | Contents |
|---|---|
| [plan.md](plan.md) | Core design, phases and current status |
| [docs/mcp.md](docs/mcp.md) | Client setup, tool loop, approvals and manual validation |
| [plan_mcp.md](plan_mcp.md) | MCP server: docking modes, tools, safety, phases |
| [docs/architecture.md](docs/architecture.md) | Components and data flow |
| [docs/templates.md](docs/templates.md) | Writing workflow templates (short-content rules) |
| [docs/event-log.md](docs/event-log.md) | Record types and replay |
| [docs/security-model.md](docs/security-model.md) | Isolation levels and their limits |
| [docs/providers.md](docs/providers.md) | Model providers and roles |
| [docs/install.md](docs/install.md), [docs/releasing.md](docs/releasing.md) | Install channels; author-only release setup |
| [docs/m7-vm-brain-mode.md](docs/m7-vm-brain-mode.md) | Manual end-to-end test on a fresh VM with Claude Code in brain mode |
| [docs/testing.md](docs/testing.md) | Running the offline tests (prime the uv cache once: `uv run python scripts/prime_test_cache.py`) |
| [docs/DECISIONS.md](docs/DECISIONS.md), [CHANGELOG.md](CHANGELOG.md) | Decisions and history |
