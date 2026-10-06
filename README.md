# MLCA v2

MLCA guides a machine learning project through declared workflow events. A Navigator proposes useful
actions; a Worker writes standalone analysis scripts. The engine controls gates, scope, artifact
provenance, validation loops and test access. CLI and Textual clients share the same Session API.

P0–P8 source implementation is present. **Runtime validation is deferred**: no smoke, full-cycle,
provider or UI tests have been run. See [implementation status](docs/IMPLEMENTATION_STATUS.md),
[decisions](docs/DECISIONS.md) and the original [plan](plan.md). Workflow content is DRAFT.

## Installation

Python 3.11+ and uv are required. From this repository:

```bash
uv sync --group dev
uv run mlca --version
uv run mlca
```

The commands above are instructions for use; application execution has not been performed in this
implementation session. Linux bubblewrap is required for level A. Other systems require explicit
opt-in to weaker trusted-code execution; read the [security model](docs/security-model.md).

## Configuration

Use `mlca config edit` or copy [examples/config.yaml](examples/config.yaml) into
`~/.config/mlca/config.yaml`, replacing model placeholders. Credentials come from environment variables.
OpenAI API, OpenRouter and OpenAI-compatible/local providers are supported. Models and provider choices
can differ between roles. No prices or default models are assumed. Real calls require pricing or a
configured request-cost bound. Inspector is optional. Account login and special free-model gateways
are reserved for P9. See [provider guide](docs/providers.md).

## A project

```bash
uv run mlca init /path/to/project --data /path/to/dataset.csv \
  --template tabular_classification --brief-file /path/to/brief.yaml
uv run mlca --project /path/to/project status --json
uv run mlca --project /path/to/project options --json
uv run mlca --project /path/to/project choose 1
uv run mlca --project /path/to/project confirm brief_confirmed "Study brief reviewed"
uv run mlca --project /path/to/project next
```

The TUI supplies equivalent forms and actions. Supported templates are tabular_classification and
survival. Events: onboard → data → eda → split → preprocess → features → model → validate → test →
interpret → report. Validation loops return to preprocessing/features/model until test exposure.
Custom instructions must pass deterministic scope checks and Navigator classification.

The engine freezes partitions. In the test event, `unlock-test` requires typing `UNLOCK TEST` and a
reason. Test files are temporarily exposed only to authorized test-reading actions. Re-unlocks are
recorded; fitting closes after project-wide test exposure. Domain experts still review target
construction, observational units, preprocessing semantics and validity of interpretations.

## Evidence and resumption

Project state lives under `.mlca/`: append-only log, frozen template, analysis environment and package
lock, immutable completed steps, encrypted test partition and request evidence. Numbered scripts,
figures, tables, reports and PROJECT_LOG.md are materialized views. Their edits are detected and never
silently overwritten. `branch NAME --from ID` and `checkout NAME` select alternative histories.

```bash
mlca log --verify
mlca replay                 # pure state rebuilding
mlca replay --verify        # explicit script execution in a new environment
mlca report all             # deterministic reports, no model calls
mlca usage
mlca doctor
```

Replay distinguishes state reconstruction from numerical reproducibility. Mismatches are reported.
No fresh LLM call is represented as reproduction. See [event log](docs/event-log.md),
[architecture](docs/architecture.md), [template guide](docs/templates.md) and [lineage](docs/lineage.md).

The paper, legacy code/data and reference harnesses were not edited. New harness evidence must remain
separate from legacy study results. No remote or publication is configured. License remains an author
decision; the placeholder grants no license.
