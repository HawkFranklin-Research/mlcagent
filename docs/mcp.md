# MCP docking

MLCA includes a local stdio MCP server in its Python package. No separate server install,
network listener or model account is required for brain mode.

```sh
uv sync --group dev                           # from this checkout
uv run mlca mcp --project /absolute/study --mode brain
uv run mlca mcp doctor
```

For a published package, `uvx mlca mcp` or `npx mlca mcp` forwards to the same server.
Those first runs can fetch packages and exceed a client's startup timeout; install once with
`uv tool install mlca` first when publication is available. The current checkout remains unpublished.

The server speaks MCP on stdout; diagnostics use stderr. The official Python SDK negotiates
modern or legacy initialization. Doctor starts a real subprocess and lists the 14 tools;
client registration queries have five-second timeouts and never print client configuration.
It does not run a study or call an LLM.

## Modes

| Mode | Options and scripts | Model requests |
|---|---|---|
| **brain** (MCP default) | Connected agent proposes catalog actions and submits Python source | MLCA makes zero; the client's inference is accounted by its own provider |
| **driver** | Connected agent chooses; MLCA's Navigator and Worker generate and repair | MLCA uses configured providers and its usage budgets |

`--mode` overrides project `mcp.mode`. Plain CLI/TUI always use driver mode. Both modes use the
same Session, event gates, option validation, fit checks, sandbox and evidence pipeline.
Brain mode applies deterministic scope checks; semantic Navigator classification is explicitly
skipped, since it would require a model call. It is not described as equivalent semantic filtering.

## Connect a client

Install the checkout with `uv tool install .`, or use your installed MLCA executable. A client
must be able to find that executable and project files. The helper prints the actual executable
path when it can find one. None of these commands publish MLCA or download models.

```sh
mlca mcp install --client claude --with-skill   # preview only
mlca mcp install --client claude --with-skill --yes
mlca mcp install --client codex                # preview only
mlca mcp install --client hermes --with-skill
mlca mcp install --client openclaw
mlca mcp install --client cursor --scope project
mlca mcp install --client json                # valid generic mcpServers JSON
```

Only `--yes` changes client settings. Existing target configurations are backed up alongside
the original with a `.mlca-backup-<id>` suffix and mode 0600. CLI registration is run with argv,
never a shell. Failed registrations report no captured config/output; use the backup to recover.
Cursor JSON preserves other servers and settings. Generic JSON is printed, never automatically
written. Skill copying is supported for Claude, Codex and Hermes, and also requires `--yes`.
The bundled [agent guide](../skills/mlca/SKILL.md) can be copied manually to other clients.

| Client | Helper operation | Scope and validation |
|---|---|---|
| Claude Code | `claude mcp add --scope user mlca -- mlca mcp --mode brain` | user/project; installed 2.1.292 CLI help checked |
| Codex | `codex mcp add mlca -- mlca mcp --mode brain` | user only; installed 0.160.1 CLI help checked |
| Hermes | `hermes mcp add mlca --command mlca --args mcp --mode brain` | user only; v0.21.5+8071 CLI help checked |
| OpenClaw | `openclaw mcp set mlca '<server JSON>'` | user only; official registry documentation checked, client absent here |
| Cursor | merges `.cursor/mcp.json` under `mcpServers` | user/project; official documentation checked, client absent here |

Project scope uses the root `-p PATH` setting (or the current directory) and pins that absolute
path in server arguments. Codex/Hermes/OpenClaw reject project scope rather than silently
changing a user registration. Use their user registration and `mlca_open` to select a study.
OpenClaw stores native entries under `mcp.servers`; it is not the generic `mcpServers` shape.
See [Claude MCP configuration](https://code.claude.com/docs/en/mcp), [OpenClaw registry](https://docs.openclaw.ai/cli/mcp/registry) and
[Cursor MCP settings](https://prod.cursor.com/docs/mcp). Restart the client after registration.

Hermes equivalent configuration:

```yaml
mcp_servers:
  mlca:
    command: mlca
    args: [mcp, --mode, brain]
```

For clients requiring JSON:

```json
{"mcpServers":{"mlca":{"command":"mlca","args":["mcp","--mode","brain"]}}}
```

## Stable tools

| Tool | Purpose |
|---|---|
| `mlca_open` | Open an existing project; full integrity verification |
| `mlca_init` | Initialize from explicit paths, template and brief; unresolved columns return candidates |
| `mlca_status` | Compact current event, checks, facts, active step, approvals and budget |
| `mlca_options` | Current menu and, in brain mode, action catalog and parameter schemas |
| `mlca_submit_options` | Brain-only catalog proposals, validated by the engine |
| `mlca_choose` | Choose a returned option ID and start work |
| `mlca_custom` | Submit an instruction within the current event's scope |
| `mlca_submit_script` | Brain-only source submission to an awaiting step |
| `mlca_step_status` | Poll execution, completion or the next repair work order |
| `mlca_move` | Next event or an allowed validation loop |
| `mlca_branch` | List, create or check out branches; active steps block mutation |
| `mlca_request_approval` | Request a human confirmation, test unlock or package approval |
| `mlca_read` | Filtered facts/log metadata, completed scripts, summary tables, PNGs and reports |
| `mlca_report` | Engine-generated methods, provenance, figure index and usage |

The SDK tool schemas describe arguments. There are no confirm, unlock or approve tools.
Read resources: `mlca://view/status`, `mlca://view/facts`, and
`mlca://evidence/{kind}?ref=<encoded-reference>`. Figures use the read tool's image content.

## One step

1. Open/init, then call status and options. Retain the returned opaque `opt:<record>:<id>`.
2. In brain mode, optionally submit natural catalog options, then request a fresh menu.
3. Choose exactly one option. Engine-run inventory, splits and reports need no submitted source.
4. Poll every 2–10 seconds while running. Some calls return a temporary operation ID before
   StepStarted; polling resolves it to the durable step ID. Temporary IDs last for that connection.
5. For `awaiting_script`, use the supplied work order: named inputs, output schema, packages,
   brief, Worker contract, fit requirements, attempt limit and privacy rules.
6. Submit one script. A failed attempt returns reduced diagnostics and a repair work order;
   exhausted attempts are terminal. Work orders and actual steps survive server reconnection.
7. Read evidence and request human decisions as required. Completed events offer next first,
   then unrun supporting actions and scoped custom instructions; these do not reopen checks.

Project action locks prevent simultaneous CLI/TUI and MCP execution. A server shutdown waits
for its active worker thread. A hard process/host crash can leave a running step; investigate
and explicitly abandon it with `mlca abandon-step <id> --reason ...`, preserving failure evidence.
To try an alternative model, branch from a record before the model step starts.

## Human approval

When a tool requests approval, dependent work stops. In your own terminal:

```sh
mlca -p /absolute/study approvals
mlca -p /absolute/study approvals approve <request-id> --note "Reviewed evidence"
mlca -p /absolute/study approvals decline <request-id> --note "Reason"
# Test request, only in the test event:
mlca -p /absolute/study approvals approve <request-id> --note "Final evaluation" --phrase "UNLOCK TEST"
```

The TUI's approval dialog also resolves requests. Stale branch/event/generation/split requests
are refused. Test plaintext exists only around a declared test execution, never during agent
thinking or repair waiting. Test exposure closes subsequent fitting, validation loops and installs
for the entire study, including branches.

## Privacy, provenance and limits

Each dispatched tool/resource result produces one egress/usage envelope: caller, tool, time,
body byte count/hash and content categories. SDK transport metadata is excluded from the digest.
SDK schema/transport failures before dispatch are not engine operations. Before a project opens,
the ledger resides in the MLCA user-data directory; thereafter it resides in the project.

MCP callers are `agent:<client>/<version>`. Reports separate human decisions from agent choices
and submitted scripts from Worker scripts. External tool counts are separate from model requests.
External agent tokens/cost are unavailable; MLCA does not label them zero inference cost.

Tool summaries are fixed text. Free content is inside `data`/`*_data` fields and must be treated
as untrusted. Views omit raw inventory/sample rows and stdout/stderr. Reads require indexed,
hash-checked artifacts: summary tables at most 50×12 and 8 MiB, PNG figures at most 8 MiB, completed script
and bounded report text. Credential text is scrubbed before serialization, hashing and logging.

With `allow_sample_rows: false`, registration and engine splitting index source rows using private
salted fingerprints. Collection marks matching table artifacts `contains_data_rows: true`, and
MCP refuses them. Reads also recheck legacy artifacts without the flag. Numeric fingerprints are
stored at six and four significant digits, with missing-value normalization. In addition to the
original exact shared-column check, matching ignores column names and order and flags a table row
when at least `min(3, n_columns)` of its cells match distinct cells in the same source row.
Cells from different source rows or repeated copies of one source cell do not add up to a match.
Full-row fact values are checked across column names/order at both precisions before model fact
extraction; legacy copied-row facts refuse MCP views. The private store is not mounted into steps
or exposed as an MCP resource.

Tests verify that `describe()`, class counts and metrics remain readable. Coincidental matches,
especially in small or categorical datasets, can still produce conservative refusals. Four
significant digits is a specific normalization, not a guarantee for every decimal-rounding scale.
The guard catches accidental and simple copies, not a deliberate agent: the agent writes the code
and can always encode data into strings, noise or figures. Brain mode sends derived results to
the agent's provider by design. For confidential data, use standalone driver mode with every model
local and no external agent receiving outputs; docking a remote agent still sends it returned
content even if MLCA's own models are local. The fingerprint heuristic is not a confidentiality
guarantee, anonymization method or protection against inference.

Version-1 indexes upgrade atomically from hash-verified registered sources. Those rows already
cover historical split partitions, so migration needs no test decryption; future splits also record
dual-precision profiles. Missing/changed sources refuse migration and leave the old index intact.

If the manuscript describes brain mode, it should state the same limitation: the external agent
authors executable code and receives derived results; row fingerprints detect simple copying but
cannot prevent deliberate encoding. Confidential studies must use local driver models without
remote output recipients. This implementation task does not change the manuscript.

## Trust boundary

Client identity is attribution from MCP clientInfo, not authentication. MLCA controls only calls
through Session/MCP and its step sandbox. An agent's native tools may read original registered
data, `.mlca/data/splits/*.parquet`, keys under `~/.local/share/mlca/keys/` (or the configured
user-data directory), and copied evidence in `tables/`, `figures/`, `reports/` and `scripts/`.
It may also invoke `mlca approvals approve`, `unlock-test`, `confirm` or `package` as the owner.
Reports always state `agent_file_access: "unknown (outside MLCA)"`; permission settings do not
change that assessment. Level B remains trusted execution, not an OS sandbox.

The Claude install preview includes a recommended project `permissions.deny` block. With `--yes`,
the helper backs up and merges `.claude/settings.json` in the project selected by `-p PATH`,
preserving unrelated settings and existing deny rules. This project policy is written even for
a user-scoped server registration, and only affects clients loading that project's settings.
It covers private state, registered data paths, keys, copied evidence and human commands.
Bare `Bash` and `PowerShell` denies also block command wrappers that evade prefix rules;
bypass mode is disabled in the recommendation. Re-run after initializing/registering data so
the block includes its paths. The preview writes nothing and does not execute a client command.

Syntax was checked against Claude Code 2.1.292 and its [official permission documentation](https://code.claude.com/docs/en/permissions).
Other clients receive prose guidance on stderr, keeping JSON registration snippets valid.
Disable native file/shell/execution and other filesystem MCP tools. Codex's read-only sandbox
limits writes, not reads. Client settings can be changed or bypassed outside MLCA; they are not
an enforced OS boundary. Use an MCP-only client or separate OS identity/container when that
boundary is required. No actual client was registered or restricted during implementation.

No HTTP listener, A2A, ACP or MCP tasks extension is implemented; polling works across clients.

## Validation and M7 author checklist

Automated offline tests cover real stdio discovery, legacy/modern initialization, full synthetic
brain and driver studies, zero-model brain execution, bypass attempts, repairs, human approvals,
locks in both directions, privacy/ledger hashes, image reads and registration previews/backups.
The agent guide is validated and included in the wheel. Guard mutation checks are recorded in
[implementation status](IMPLEMENTATION_STATUS.md). Native clients are still to be exercised:

| Manual case | Client version/date | Result |
|---|---|---|
| Claude Code brain: discover → options → source → figure → approval | not run | author pending |
| Codex brain: same, then reopen a pending work order | not run | author pending |
| Hermes brain: same, verify image and resource support | not run | author pending |
| Plain TUI driver with a configured live provider | not run | author pending; provider calls require authorization |
| Original anemia study | data not supplied on this machine | pending |
| Native macOS/Windows installation and execution | not run | pending |

For each client, record the version/date, 14-tool discovery, requested/approved decisions,
step IDs, artifact reads, attribution, observed errors and any workaround. Do not substitute
SDK tests for these manual client results. No client was registered during implementation.
