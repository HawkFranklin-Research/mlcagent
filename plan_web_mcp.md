# mlcagent-web-mcp: brain mode for the browser edition (follow-up plan, stage 1)

A follow-up to `plan_web.md`. It keeps **brain mode open for the browser edition**: an external agent (Claude Code, Codex, Hermes, OpenClaw, or an agent built into the browser) connects to a running MLCA **browser tab** and drives the study there. The agent chooses options and writes step scripts, and the steps run inside the visitor's browser.

This is a **different server** from the native one (`mlca mcp`, `plan_mcp.md`). Its name is **`mlcagent-web-mcp`**.

**Status of this plan: stage 1, mapping only.**
- It records what the native MCP server does today, the action items the web version should offer, and the open transport choices.
- After the first browser-edition code exists (`plan_web.md` through W8), revise this file with the specifics: where each tool connects, the transport chosen, and the security details.
- Until then, **implement nothing here except WM0** (section 6).

Written 2026-10-12. Rules of `plan.md` §0 and `plan_mcp.md` apply.

---

## 1. Principles carried over unchanged

1. **Same tools, same meaning.** Tool names, arguments and results match the native server wherever the action exists in both. A skill or prompt written for `mlca mcp` works on `mlcagent-web-mcp`. Web-only tools get a `web_` prefix.
2. **The engine decides, the agent only proposes.** Options are validated against the catalog. Scripts pass the same static checks, the step sandbox (level W in the browser), the fit rules and the test lock. Gates and sub-goal checks are code.
3. **Human-only decisions stay human-only:** confirming sub-goals, unlocking the test set, approving packages. They are never exposed as tools; the agent can only **request** them, and the person at the browser approves in the web UI.
4. **Attribution:** every agent action is recorded as `agent:<client>/<version>`; the person in the tab is `user`.
5. **Privacy:** results sent to the agent follow `privacy.allow_sample_rows`, the row-copy guard, and the egress log, as in native MCP.
6. **One driver at a time per project.** While an agent is connected, the UI shows "Agent connected: <client>", the person can watch every action live, and one click disconnects it.

---

## 2. What the native MCP server does today (`src/mlca/mcp/server.py`)

| Native tool | Purpose | Web equivalent | Notes for the web version |
|---|---|---|---|
| `mlca_open(path)` | open a project on disk | `mlca_open(project_id)` | projects live in the browser's private storage; identified by id or name, not a path |
| `mlca_init(path, data, template, brief)` | create a project from files | `mlca_init(name, data_refs, template, brief)` | **an agent cannot read the visitor's disk.** `data_refs` must name files already attached in the tab (see `web_request_data`) |
| `mlca_status()` | event, sub-goals, facts, branch, active step, approvals, budget | same | unchanged |
| `mlca_options()` | current options (+ catalog in brain mode) | same | unchanged |
| `mlca_submit_options(options)` | agent proposes catalog options (brain) | same | unchanged |
| `mlca_choose(option_id)` | start a step; returns step id and work order | same | unchanged; the step runs in the browser step sandbox |
| `mlca_custom(text)` | scoped custom instruction | same | unchanged |
| `mlca_submit_script(step_id, code)` | agent's script for the awaiting step (brain) | same | unchanged; sandbox level W |
| `mlca_step_status(step_id)` | progress, work order, diagnostics | same | unchanged |
| `mlca_move(to)` | next event or validation loop | same | unchanged |
| `mlca_branch(action, name, from_id)` | create, checkout, list branches | same | unchanged |
| `mlca_request_approval(kind, target, reason)` | ask the human for a confirmation, test unlock or package | same | the approval appears in the tab; the person clicks approve/decline (unlock still needs the typed phrase) |
| `mlca_read(kind, ref)` | figure (image), script, table, log, facts, report | same | read from browser storage; same row-copy guard |
| `mlca_report(kind)` | regenerate reports | same | unchanged |
| resources `mlca://view/{kind}`, `mlca://evidence/{kind}{?ref}` | status/facts views, evidence reads | same URIs | unchanged |
| server instructions | the tool loop and the rules | same text plus a note on web differences | unchanged where possible |
| native-only: `mlca mcp install`, client permission blocks, `mlca mcp doctor` | register the server with a client | replaced by **pairing** (section 4) | |

---

## 3. Action items wanted for the web version (beyond the native set)

Candidates for stage 2 to confirm, change or drop:

| Proposed tool | Action | Why | Human-only part |
|---|---|---|---|
| `web_list_projects()` | list projects in this browser (id, name, template, current event, last activity) | there is no folder to browse | — |
| `web_request_data(description)` | ask the person to attach a data file (file picker in the tab) | the agent cannot read the disk | the person picks the file |
| `web_list_data()` | attached files with name, size, sha256, columns (no rows) | to call `mlca_init` with valid refs | — |
| `web_export_project(project_id, include_data)` | build an export zip and offer it in the tab | moving a study to native for `replay --verify` | the person saves the download |
| `web_metrics(project_id)` | return `metrics.json` | agent-level numbers for the paper or a report | — |
| `web_bench_status(bench_id)` | progress of a running bench | bench runs in the tab | starting a bench stays a UI action (it spends the person's budget) |
| `web_runtime_info()` | Pyodide version, package bundle, sandbox level W, permission mode, WebGPU availability | the agent should know what the runtime can do before writing scripts | — |
| `web_ui_focus(target)` | bring a panel or figure into view for the person (e.g. "show Figure 3") | lets the agent guide the person's attention | — |
| `web_session_info()` | who is connected, since when, which project | transparency | — |

**Never tools, in the web version either:**
- confirm, unlock test, approve package;
- change the permission mode or the network allow-list;
- enter or read API keys;
- delete projects or data;
- change budgets.

---

## 4. Transport: open choices (decide in stage 2, after `plan_web.md` W8)

A browser tab cannot accept incoming connections, so the agent reaches it in one of these ways:

| Option | How it works | Fits | To verify |
|---|---|---|---|
| **A. WebMCP** | the page registers its tools with the browser (`document.modelContext`); agents built into the browser call them | in-browser agents (e.g. Chrome's assistant, extensions) | WebMCP was a Chrome origin trial with a renamed API in 2026; check stable support at the time |
| **B. Relay** | the tab opens an outbound WebSocket to `mcp.mlcagent.hawkfranklin.in`, which exposes a remote MCP endpoint (Streamable HTTP) to the agent | Claude Code, Codex and Hermes anywhere (`claude mcp add --transport http …`) | needs a small hosted service; pairing code and token; the relay passes messages, holds no project data |
| **C. Local bridge** | a tiny native command (`mlca web-bridge`) is the stdio MCP server for the agent and talks to the tab over a localhost WebSocket | Claude Code or Codex on the same computer, no hosted service | browser rules for an HTTPS page connecting to `localhost` (Private Network Access prompts); needs MLCA installed natively, which partly defeats "no install" |
| **D. Browser extension** | an extension bridges the agent and the tab | power users | extension store review; least preferred |

**Default leaning, to confirm in stage 2:** B for external agents, A when WebMCP is stable. C is a fallback for offline use.

**Pairing** (B and C):
1. The person clicks "Connect an agent" in the tab.
2. The tab shows a one-time code and the exact `claude mcp add …` / `codex mcp add …` command.
3. The connection carries the code-derived token.
4. The tab shows the connected client; disconnect revokes the token.

---

## 5. Architecture direction

Refactor the native server's controller (`mlca/mcp/server.py: Controller`) into a **transport-agnostic tool layer** (`mlca/mcp/tools.py`). It holds the handlers, result shaping, privacy filtering and accounting. Then:
- the native stdio server uses it as today;
- in the browser, the same module runs inside the engine worker (Pyodide), and a thin JavaScript adapter connects it to the chosen transport.

The privacy guard, attribution and egress logging are therefore identical by construction.

---

## 6. Phases (stage 1 → stage 2)

| Phase | Content | Done when |
|---|---|---|
| **WM0** (now allowed, small) | Extract the transport-agnostic tool layer from `mcp/server.py` (no behaviour change); this file's section 2 table re-checked against the code | native MCP tests unchanged and green; `tools.py` has no transport imports |
| *(gate)* | `plan_web.md` W1–W8 done; revise this plan to **stage 2**: pick the transport, final tool list, pairing and security design | author approves the revised plan |
| WM1 | Tool layer running in the browser engine worker; in-page test harness calls tools directly | Playwright: brain-mode study (scripts submitted through the tool layer) completes in the tab |
| WM2 | Chosen transport (A, B or C) + pairing + connected-agent banner | a real client connects and drives a fixture study |
| WM3 | Web-only tools (section 3, as confirmed) | tests per tool |
| WM4 | Parity and bypass suite: the native MCP bypass tests re-run against `mlcagent-web-mcp` (human-only refusals, catalog-only options, layer-1 scope, sandbox denials, row-copy guard, attribution) | all pass; differences documented |
| WM5 | Docs: `docs/web/mcp.md` (connect, pair, what the agent can and cannot do), skill update (`skills/mlca/SKILL.md` notes web differences) | reviewed |

## 7. Review checklist (stage 2)
1. Tool names and results match native where the action exists in both.
2. No human-only action is reachable through any tool, transport or UI shortcut driven by the agent.
3. The relay (if chosen) never stores project data or keys; pairing tokens expire and revoke.
4. The bypass suite passes against the web server.
5. The person in the tab sees every agent action live and can disconnect in one click.

## Status
- **2026-10-12:** stage 1 written (mapping and options). Only WM0 may start; the rest waits for `plan_web.md` W8 and the stage-2 revision.
