# MLCA browser edition (driver mode in WebAssembly): implementation plan

Plan for a coding agent. It adds a **browser edition** of MLCA: a static website (`mlcagent.hawkfranklin.in`) where the whole driver-mode harness runs inside the visitor's browser, on their own CPU and memory, with no installation. **Brain mode stays native and unchanged** (`mlca mcp`; `plan_mcp.md`).

Written 2026-10-12. Companion to `plan.md` (core), `plan_mcp.md` (native MCP) and `plan_web_mcp.md` (brain mode for the browser edition, `mlcagent-web-mcp`, follow-up); read their sections 0–3 first. Every rule in `plan.md` §0 applies: tests offline, no hard-coded models, local commits only, nothing published or deployed without the author's go-ahead. Record decisions and deviations in `docs/DECISIONS.md`.

**Branching:** do all work on a branch `web-edition`. The version used for the paper's measurements (the code freeze, see the paper repository's `REVISION_JOURNEY.md` Stage 4) must stay untouched on `master`. Merge only when the author says so.

---

## 0. Goal and non-goals

**Goal.** A user opens the site, enters their own model API key (or picks an in-browser model), picks a data folder or uploads a table, and runs a complete guided study:
- the same workflow templates, events, options and custom instructions;
- the same gates, sub-goal checks, scope guard, test lock and fit rules;
- the same event log, reports, `metrics` and `bench`.

Every analysis step runs as Python inside the browser.

**The native/browser contract.** The browser edition must produce the **same event log format**. A project exported from the browser opens natively, and `mlca replay --verify` and `mlca metrics` work on it. The engine code (`engine/`, `log/`, `templates/`, `report/`, `evaluation/`, `roles/`) is **shared, not forked**. Only the operating-system layer differs.

**Not in scope** (state these in the docs):
- brain mode for the browser edition in this plan: it is planned separately in `plan_web_mcp.md` (`mlcagent-web-mcp`), and this plan only keeps the engine ready for it;
- Docker, Linux emulation (container2wasm, v86);
- CUDA and PyTorch: browsers never expose CUDA, and PyTorch is not built for Pyodide. **GPU work goes through WebGPU instead, in phase W10** (section 4.7);
- packages with native code that Pyodide does not build;
- access to the computer beyond files and folders the user grants;
- datasets that need more than about 4 GB of memory in one worker.

---

## 1. Facts this plan relies on (re-check in W0)

- **Pyodide** (CPython in WebAssembly) provides, as of October 2026:
  - built in: numpy, pandas, scipy, scikit-learn, statsmodels, matplotlib, pyarrow, xgboost, lightgbm, cryptography, pydantic, pyyaml, rich, httpx;
  - **not** built: seaborn, lifelines, shap, numba, torch.

  Pure-Python packages may install with `micropip` (seaborn and lifelines need testing). Source: pyodide.org, "Packages built in Pyodide".
- No subprocesses, sockets or threads in the usual sense. Workers are the unit of isolation, and network goes through the browser's `fetch` / XHR.
- WebMCP (pages exposing tools to agents) is an origin trial whose API surface was renamed in 2026. Not used.
- Model providers callable from a browser with the user's key: OpenAI, OpenRouter, Anthropic (requires its direct-browser-access header), and local OpenAI-compatible servers if they allow the site's origin (Ollama via `OLLAMA_ORIGINS`).

---

## 2. Architecture

```
mlcagent.hawkfranklin.in  (static hosting; cross-origin isolated: COOP same-origin, COEP credentialless)
│
├── UI thread (TypeScript)            web/src/ui/…   screens mirroring the TUI
│     └── bridge (postMessage)        web/src/engine/bridge.ts
│
├── Engine worker (Pyodide)           web/src/engine/engine.worker.ts
│     ├── mlca wheel (src/mlca, mlca_runtime, templates, styles, assets), unchanged engine code
│     ├── mlca.platform.browser       storage, locks, HTTP, runner, environment, machine info (section 3)
│     ├── project storage             OPFS (browser private file system) per project; registered data copied in
│     └── model calls                 fetch to OpenAI / OpenRouter / Anthropic / local server; or WebLLM (W9)
│
└── Step host: sandboxed iframe       web/src/steps/step-frame.html  (sandbox="allow-scripts", no allow-same-origin → opaque origin)
      └── Step worker (fresh Pyodide per attempt)  web/src/steps/step.worker.ts
            gets: script, declared inputs (bytes), package bundle (bytes), env (MLCA_*), timeout
            returns: outputs/ files, manifest.json, stdout/stderr (capped), exit status
            CSP: connect-src 'none' (Sandboxed mode) · no storage · no access to the engine's origin
```

Why this isolation works:
- the step runs in an **opaque origin**, so it cannot reach the engine's storage (vault key, other projects);
- its **file system contains only what the engine copied in** (declared inputs), the browser equivalent of bubblewrap's binds;
- the **content-security policy blocks the network** even if step code reaches JavaScript through Pyodide's `js` module.

Static checks (`runner/static_checks.py`) add `js`, `pyodide` and `pyodide_js` to the forbidden imports in the browser profile, as defence in depth.

---

## 3. The platform layer (shared code, two implementations)

Create `src/mlca/platform/` and route every operating-system call through it. The native implementation wraps today's code exactly, so native behaviour and tests stay unchanged.

| Interface (`platform/base.py`) | Native (`platform/native.py`): today's code in | Browser (`platform/browser.py`) |
|---|---|---|
| `Dirs`: user config, data and keys directories | `paths.py` (`XDG_*`) | fixed OPFS paths (`/mlca/config`, `/mlca/data`, `/mlca/keys`) |
| `Lock`: exclusive project lock with timeout | `filelock.FileLock` in `log/store.py`, `api.py: mutation`, `llm/client.py`, `privacy/rows.py` | Web Locks API (`navigator.locks`) via the bridge; one engine per tab, so locks also guard against a second tab |
| `Http`: POST JSON, return status/headers/body, timeout | `openai` SDK / `httpx` in `llm/providers/*.py` | synchronous request from the engine worker (see W0 decision on the sync bridge) |
| `Runner`: run one step attempt with declared inputs, timeout, network flag; return the `RunFinished` payload | `runner/process.py` + `sandbox/bwrap.py` / `audit_hook.py` | message to the step host; waits for the result (W0 decision) |
| `Environment`: create/lock the analysis environment; install an approved package; report versions | `project/env.py` (`uv`) | Pyodide version + pinned package bundle; `micropip` for approved pure-Python packages; lock = bundle manifest with sha256 |
| `MachineInfo`: CPU, RAM, GPU, OS, versions for the run snapshot | `evaluation/snapshot.py` | `navigator.hardwareConcurrency`, `deviceMemory`, user agent, WebGPU adapter info if present, Pyodide version |
| `SandboxLevel` | `sandbox/level.py` (A/B) | new level **`W`** ("browser worker isolation"), recorded in every `RunFinished` and documented in `docs/security-model.md` |
| `Clock` | `time` / `datetime` | same (works in Pyodide) |

**Rules:**
- No module outside `platform/` imports `subprocess`, `filelock`, `shutil.which` or `httpx`/`openai`, or reads `sys.platform`, after W1. Add a unit test that greps for this.
- The sqlite row-fingerprint store (`privacy/rows.py`) uses the standard `sqlite3` module (available in Pyodide). Its file lives in project storage like any other.
- CLI (`cli/`), TUI (`tui/`), MCP (`mcp/`), `web.py` and `distribution.py` stay native-only. They are not packaged into the browser wheel.

---

## 4. Browser specifics

### 4.1 The synchronous bridge (decide in W0)
The engine is synchronous Python (`Session.choose()` runs a step and returns). In the browser, model calls and step runs are asynchronous. Choose **one**, and record it with measurements in `docs/web/SPIKES.md`:
- **(A) JSPI:** Pyodide's `run_sync` on JavaScript Promise Integration. Simplest code, but check the browser support matrix.
- **(B) SharedArrayBuffer + `Atomics.wait`** in the engine worker, with the UI thread performing fetches and step runs. Needs cross-origin isolation, which the hosting headers provide.
- **(C) Async engine API:** make `Session` methods awaitable in the browser path only. Most invasive; use only if (A) and (B) fail.

Preference: A if Chrome, Edge and Firefox stable support it, otherwise B.

### 4.2 Packages
- Pin one Pyodide release. The browser runtime bundle: numpy, pandas, scipy, scikit-learn, statsmodels, matplotlib, pyarrow, xgboost, lightgbm, plus `mlca_runtime`. Test seaborn and lifelines via `micropip`. If lifelines fails, the survival template is marked "native only" in the browser registry.
- The engine fetches packages once (the browser cache and service worker keep them). For each step, it **passes the wheel bytes to the step worker**, which unpacks them without network.
- Template field `default_runtime_packages` is checked against the browser bundle at project creation. A template needing an unavailable package is refused with a clear message.

### 4.3 Storage and data
- Each project is a folder in OPFS with the same layout as native (`.mlca/`, `scripts/`, `reports/`, …), mounted into the engine's Pyodide file system (`mountNativeFS` or equivalent; confirm in W0). Persist after every mutation.
- **Data registration:** the user picks files (File System Access API in Chrome/Edge; plain upload elsewhere). Files are **copied** into project storage at registration, with sha256 recorded, so later steps never touch the user's disk.
- **Export / import:** a project as a zip (log, steps, views, reports; data optional). It must import natively (`mlca import` or unzip) and pass `mlca log --verify` and `mlca replay --verify`.
- Warn above 1 GB of registered data; refuse above the measured limit (W0).

### 4.4 Vault and keys
- The test-partition key is stored in the engine origin's storage (IndexedDB, or OPFS `/mlca/keys`), never inside the project folder and never sent to a step except as decrypted test data for `reads_test` steps after unlock.
- **Model API keys:**
  - entered in the settings screen and stored in the engine origin's IndexedDB;
  - never written to the event log, reports or exports;
  - redaction applies (the existing `config.redact` path);
  - a "forget keys" button.

### 4.5 Permission modes (the browser's meaning)
Shown in settings and in the run snapshot:

| Mode | Steps may | Steps may not |
|---|---|---|
| **Sandboxed** (default) | read declared inputs, write their outputs | any network, any storage, any other project |
| **Open network** | additionally fetch from an allow-list the user enters (e.g. PyPI, a data URL) | everything else as above |

There is no "bypass all": a web page can never reach the computer's shell, other folders or processes. The help text says so plainly, and points to the native install for that. MLCA's scientific guards (test lock, fit-on-train, gates, scope guard) are identical in both modes.

### 4.6 Model providers
- `llm/providers/` gains a transport parameter; the browser uses `platform.Http`.
- Kinds in the browser: `openai_api`, `openrouter`, `openai_compatible` (local servers with CORS), `anthropic` (new; also usable natively), `fake` (tests).
- `webllm` (an in-browser model through WebGPU) is optional: phase W9.
- Usage, egress, budgets and `cost_source` work unchanged.


### 4.7 GPU (WebGPU)
Browsers give pages the GPU through **WebGPU** (compute and graphics), never CUDA. In-browser games use the GPU this way, or run on a cloud server and stream video.
- MLCA's current templates use CPU libraries (pandas, scikit-learn, xgboost, lightgbm); Pyodide's numpy has no GPU path. **These steps do not get faster with a GPU**, and W1–W8 need none.
- WebGPU is useful for **models built on JavaScript-side frameworks**:
  - local LLMs for the Navigator/Worker (WebLLM, W9);
  - neural-network inference and embeddings (ONNX Runtime Web, Transformers.js);
  - small neural-network training (TensorFlow.js WebGPU backend).
- W10 explores a GPU path for a future neural-network template. A step would hand a model definition and data to a WebGPU worker through a small `mlca_runtime.gpu` API, which records device, backend and timing in the run snapshot. Sandbox rules are unchanged.
- `web_runtime_info` / the run snapshot report whether WebGPU is available and which adapter.

---

## 5. Repository layout (additions)

```
src/mlca/platform/__init__.py  base.py  native.py  browser.py
src/mlca/llm/providers/anthropic.py
web/
  package.json  vite.config.ts  tsconfig.json  playwright.config.ts
  public/assets/            logo.png, banner (from assets/)
  src/main.ts
  src/ui/                   welcome, settings (keys, mode, budgets), projects, init (data, brief, template, columns),
                            main (events, sub-goals, options, facts, log stream, status bar), approvals/confirm, unlock-test,
                            reports, figures, metrics, bench, export/import
  src/engine/engine.worker.ts  bridge.ts  protocol.ts
  src/steps/step-frame.html  step.worker.ts  protocol.ts
  src/storage/opfs.ts  keys.ts
  src/llm/webllm.ts          (W9, optional)
  scripts/build-wheel.mjs   builds the mlca wheel for Pyodide (browser profile: excludes cli/tui/mcp/web/distribution)
  tests/                    Playwright: boot, project lifecycle, sandbox, parity, UI
hosting/firebase.json       headers (COOP/COEP, CSP for the step frame, cache), rewrites
docs/web/                   README.md (user guide), SPIKES.md (W0 results), SECURITY.md (level W), PARITY.md
```

UI technology: TypeScript with Vite and a small view library (Preact or plain DOM); no server. Visual style follows the TUI: dark theme, logo banner, the same panel layout and key shortcuts (`1`–`3`, `n`, `c`, `f`, `t`, `q`).

---

## 6. Phases

Each phase ends with:
- tests green, with the native suite (`uv run pytest -q`) **unchanged and green**;
- Playwright tests for web phases;
- ruff, and `tsc` / eslint for `web/`;
- a local commit `WEB W<n>: …`;
- a status line in this file.

### W0 · Spikes (decide before building)
Small throwaway prototypes under `web/spikes/`, measured in Chrome, Edge and Firefox stable:
1. The sync bridge: A vs B (section 4.1). Round-trip latency for a model-call-sized request and a step run.
2. Pyodide in a worker inside a sandboxed opaque-origin iframe with `connect-src 'none'`. Packages installed from passed bytes; a `fetch` attempt from Python is refused.
3. OPFS mounted into Pyodide and persisted; read-back after reload.
4. `micropip` installs of seaborn and lifelines; a lifelines `CoxPHFitter` fit.
5. Performance: the anemia workflow's main step (logistic regression + RF on 1,421 rows) and a 50 MB CSV load. Compare time and memory with native.

**Done when:** `docs/web/SPIKES.md` records each result with numbers, and the decisions on the bridge, the mount method and the survival-template status.

### W1 · Platform layer, native only
Introduce `platform/` and move every OS call behind it (section 3). Pure refactor.

**Done when:** the native suite passes unchanged; the grep test passes; no behaviour change in a native golden run (`log --verify`, `replay --verify`, identical metrics fields).

### W2 · Engine in the browser (no steps yet)
Build the browser wheel; boot Pyodide in the engine worker; implement `platform/browser.py` for `Dirs`, `Lock`, `Http` (fake provider first), `MachineInfo`; mount OPFS.

**Done when:** a Playwright test, headless, creates a project from a fixture CSV and the brief, proposes options with the fake provider, records a confirmation, and reloads the page with the state intact (replay from the log).

### W3 · Step sandbox
Step host iframe and worker, package bundle passing, timeout via `worker.terminate()`, output collection into the step folder, sandbox level `W`.

**Done when** Playwright tests prove that a step script:
- runs and returns outputs, manifest, metrics and fit records;
- cannot `fetch` in Sandboxed mode, nor reach the engine's storage or the vault key;
- cannot read undeclared project files;
- is killed at its timeout;
- with Open network, can fetch only from the allow-list.

Add a `sandbox_level: W` row to `docs/security-model.md`.

### W4 · Projects, data, vault, export/import
Data registration (copy + hash), the split freeze, the encrypted test partition with the key outside the project, unlock flow, project list, export and import.

**Done when:**
- a project runs from onboard to report with the fake provider (driver mode) in the browser;
- its export imports natively and passes `mlca log --verify`, `mlca replay --verify` (native rerun of the browser-written scripts) and `mlca metrics`.

### W5 · Real providers
`Http` via the chosen bridge; providers `openai_api`, `openrouter`, `openai_compatible`, `anthropic`; key settings screen; redaction; budgets; usage and egress lines.

**Done when:**
- offline tests with a mocked fetch pass;
- a key canary scan of OPFS, exports and logs finds nothing;
- the live smoke test (one tiny structured call per configured provider) is ready, but **runs only when the author enables it**.

### W6 · Web UI
All screens in section 5, mirroring the TUI; accessible keyboard shortcuts; figures shown inline; reports viewer; metrics page (`metrics.json` rendered as tables).

**Done when:** Playwright drives the anemia-like fixture study through the UI only (choose, custom instruction accepted and refused, confirm, unlock test, report). Screenshots of each screen are saved in `docs/web/screens/`.

### W7 · Bench and parity
`mlca bench` and `bench summarize` in the browser (sequential runs in the tab, budget stop). Parity suite: the same synthetic task card in native and browser driver mode with the fake provider.

**Done when** `docs/web/PARITY.md` shows:
- identical event sequences (types and order);
- identical sub-goal outcomes, refusals and failure categories;
- metric values equal within floating-point tolerance, with differences listed and explained (e.g. package versions);
- the sandbox level differs (A vs W) by design.

### W8 · Hosting (preview only)
`hosting/firebase.json`: COOP `same-origin`, COEP `credentialless`, the step-frame CSP, long-cache headers for versioned assets, a service worker for offline reuse of Pyodide and packages, a version banner. Build script, and deploy to a **Firebase preview channel only**.

**Done when:**
- the preview URL works in Chrome, Edge and Firefox stable (the Playwright smoke suite against the preview);
- the Lighthouse load time is recorded;
- `docs/web/README.md` (the user guide) is written.

**Production** (`mlcagent.hawkfranklin.in`, DNS) needs the author's go-ahead and account access.

### W9 · In-browser model (optional, after W8)
WebLLM provider (`kind: webllm`) for Navigator and Worker, with model download on first use, WebGPU check, and a quality warning in the UI. Usage recorded with `cost_source: local`.

**Done when:** a fixture study completes with a small local model, or the failure is documented with the model id.

---

### W10 · GPU through WebGPU (optional, after W8)
1. Detect WebGPU; record the adapter in the run snapshot.
2. Spike: ONNX Runtime Web (WebGPU backend) inference and a TensorFlow.js WebGPU training loop on a small fixture (e.g. an MLP on the anemia features). Compare time with the CPU path.
3. If useful, add `mlca_runtime.gpu` (fit/predict for a declared small network, fit recorded with `fit_record` rules), and an optional neural-network action in the classification template, available only when WebGPU is present.

**Done when:** `docs/web/SPIKES.md` has the GPU measurements and the decision. If adopted, a fixture step trains on WebGPU inside the step sandbox with network blocked, and its fit evidence passes `fit_on_train_only`.

## 7. Tests (summary)
- **Native:** the existing suite, unchanged, plus the platform grep test and the native-golden equality check (W1).
- **Browser (Playwright, headless Chromium + Firefox):**
  - boot, project lifecycle, reload persistence;
  - sandbox denials (network, storage, undeclared files, timeout);
  - test lock, fit rules, scope guard refusals (zero model calls on layer-1 rejections);
  - export → native verify;
  - key canary;
  - UI flow;
  - bench.
- **Parity suite** (W7).
- CI: add a `web` job (Node + Playwright) to `.github/workflows/ci.yml`; it does not deploy.

## 8. Review checklist (used when the work is done)
1. The native suite is unchanged and green; `master` (frozen paper version) untouched; all work on `web-edition`.
2. Engine code is shared, not forked: no copy of `engine/`, `log/`, `templates/`, `report/` or `evaluation/` under `web/`.
3. No OS call outside `platform/` (grep test).
4. Step isolation proven by tests: no network (Sandboxed mode), no engine storage, no vault key, no undeclared files, timeout enforced; sandbox level `W` recorded.
5. Browser projects export into native and pass `log --verify`, `replay --verify` and `metrics`.
6. Keys never appear in logs, exports or reports (canary).
7. Unavailable packages and templates are refused clearly, not half-run.
8. Parity report written, with every difference explained.
9. Only a preview channel deployed; production waits for the author.

## 9. Open decisions for the author
| ID | Decision | Default until decided |
|---|---|---|
| WD1 | Hosting provider and domain (`mlcagent.hawkfranklin.in` on Firebase or Cloudflare) | Firebase preview channel only |
| WD2 | Which templates the web edition offers (survival depends on lifelines in W0) | tabular classification only |
| WD3 | Whether the in-browser model (W9) is wanted | not built |
| WD5 | Whether the GPU phase (W10) is wanted, and for which model types | spike only |
| WD4 | Whether the web edition's licence and terms match the package (CC-BY-NC-ND-4.0) | same as the package |

## Status
- **2026-10-12:** plan written. Not started. Start after the paper's code freeze, on branch `web-edition`.
