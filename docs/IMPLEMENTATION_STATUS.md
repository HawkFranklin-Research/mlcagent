# Implementation status — 6 October 2026

## Prompt 01 validation

Command: `uv run pytest -q` (offline tests set `UV_OFFLINE=1`, including slow tests).
Result: **40 passed in 263.43s (0:04:23)**.
`uvx ruff check src scripts tests`, `uvx ruff format --check` and `git diff --check` also pass;
Ruff's cache was explicitly directed outside the repository.

| Phase | Source implementation | Execution validation |
|---|---|---|
| P0 | Package/environment bootstrap | CLI help/version and real analysis environment creation checked |
| P1 | Event schemas, hash chain, replay, branches | Incremental/full verification, tamper messages, branch recovery, lazy sessions and 5,000 appends checked |
| P2 | Templates, checks and gates | Both template structures, any-of output checks and primary/supporting roles checked; classification gates exercised end to end |
| P3 | Project lifecycle | Inventory, structured column resolution, interactive/non-interactive init and legacy column fallback checked |
| P4 | Execution and test lock | Level A private-path/network probe; level A/B workflows, test lock, cleanup and exact fit-index refusals checked |
| P5 | Providers and request evidence | Offline fake provider, usage/egress correspondence checked; real providers remain untested |
| P6 | Roles, turn loop, Session API and CLI | Full synthetic classification path and fresh-environment standalone-script replay pass at levels A and B |
| P7 | Textual interface and reports | Welcome banner/footer, project opening, quit, readable logs and deterministic reports checked |
| P8 | Survival and hardening | Survival init/columns/template structure and post-exposure fitting refusal checked; full survival workflow remains untested |
| P9 | Later UI/account capabilities | Not implemented; Prompt 02 authorizes distribution preparation separately |

## Regression sensitivity

The required local reverts failed as expected and were restored before the passing run:

- F3: reverting checks.py caused `test_output_exists_any_of[True]` to fail with `KeyError: 'action'`.
- F6: reverting store.py caused `test_incremental_read_and_hash_chain` to fail with
  `Failed: Unexpected full log reread`.

The 5,000-append benchmark initially completed in 1.556 seconds; the permanent test enforces a 30-second
bound on this host. Tests use reviewer-derived synthetic fixtures and no API keys or original data.
Dependency priming happens before offline runs; see [testing](testing.md). A first run exceeded the
small `/tmp` quota, so test scratch lives outside the repository on the cache filesystem and projects
are cleaned after each test. That failed attempt is not counted as passing validation.

## Limits and author decisions

Original anemia data will be supplied later. These runs establish harness behavior, not scientific
case-study results. Full survival, live providers, broad UI navigation, adversarial/native-code
coverage and cross-platform execution still need validation. Template content remains DRAFT.
Licence, public package/repository names and default models remain author decisions. No remote,
tag, push, release or publication has been created.


## Prompt 02 distribution validation

Final command: `uv run pytest -q` (offline, slow tests included).
Final result: **54 passed, 1 skipped in 227.66s (0:03:47)**. The skip is PowerShell syntax/analyzer
validation: neither pwsh nor PSScriptAnalyzer is installed on this Linux host.

Prepared: dynamic Python metadata, wheel/sdist with templates/styles/derived artwork/runtime helper,
loopback-only browser TUI, portable scrubbed processes and audit paths, shell/PowerShell installers,
version-pinned npm launcher, generated Homebrew formula, cross-platform CI and gated release workflows.

Additional checks:

- Ruff lint and full format check; Git whitespace check: pass.
- `uv build` / check_wheel.py; fresh clean-home `uv tool install` and version/doctor JSON/banner: pass.
- Missing web-extra refusal and real loopback HTTP start/stop: pass.
- `node --test packaging/npm/test/`: four tests pass (arguments/pinning/debug, status, missing uv, signals).
- Shell installer fake-uv install/upgrade/pin/PATH dry runs and `sh -n`: pass.
- `npm pack --dry-run`: exactly package.json, bin/mlca.js, README.md and LICENSE.
- Homebrew dummy-hash rendering and `ruby -c`: pass. Final preview uses the local sdist hash.
- Workflow YAML syntax and licence/name/tag/sequence guard tests: pass.
- 5,000 append test under concurrent suite load: 7.576 seconds, below the 30-second bound.

Unavailable here: shellcheck, pwsh/PSScriptAnalyzer, actionlint, act and Homebrew execution; the tools
are absent. Native macOS/Windows and Python 3.11 execution were not run on this Linux/Python 3.13
host; the six-job CI matrix is prepared but not triggered. Level B is exercised locally, not presented
as native-OS validation. Full survival/original-data scientific studies and live providers remain untested.

D1 licence and D3 public name remain publication blockers. The protected GitHub environment and
registry/tap setup must be configured by the author as described in [releasing](releasing.md).
No remote, tag, push, workflow trigger, release, registration or publication was performed.

## 2026-10-07 — MCP M0

Core prerequisite regressions added: gate refusal, untrusted model completion claims, Navigator repair/fallback, zero-call deterministic scope rejection, immutable step modes, invalid fact rejection, Worker static-failure repair, budget refusal, rate-limit retry and a credential canary scan. Targeted offline run: 7 passed. Live providers remain deferred. Incoming author/reviewer edits were preserved in a separate local checkpoint.
