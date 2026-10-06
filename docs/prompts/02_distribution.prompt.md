# Prompt 02: distribution, one artefact with many installers (prepare only, never publish)

You are the coding agent for MLCA v2 in `/home/prime/Documents/github/mlca-paper-codebases/mlca-revized/`.
Read `plan.md`, `AGENTS.md`, `docs/DECISIONS.md` and `docs/prompts/01_functional_fixes.prompt.md` first.
**Start only after prompt 01 is complete and `uv run pytest -q` passes**, because the release pipeline is
gated on that suite.

## Goal

Anyone can install MLCA with one command on Linux, macOS or Windows (WSL2 recommended), from **one** build
artefact (the Python wheel and sdist). Every channel is a thin wrapper that installs that same wheel with
`uv`:

| Channel | User command | Wrapper you build |
|---|---|---|
| PyPI | `uv tool install mlca` / `pipx install mlca` | none: the wheel itself |
| Shell installer (Linux, macOS, WSL) | `curl -LsSf <url>/install.sh \| sh` | `installers/install.sh` |
| PowerShell installer (Windows) | `irm <url>/install.ps1 \| iex` | `installers/install.ps1` |
| npm | `npx mlca` / `npm i -g mlca` | `packaging/npm/` launcher package |
| Homebrew (macOS, Linux) | `brew install <tap>/mlca` | `packaging/homebrew/mlca.rb` (tap formula, template) |
| Browser view of the TUI | `mlca web` | `textual-serve`, optional extra `mlca[web]` |

**Out of scope here:** a frozen `.exe` (PyInstaller) and the Electron desktop app (plan P9). MLCA builds a
separate Python environment per project with `uv`, so a frozen binary would not remove the need for
Python and uv. The installers set those up instead.

**Hard rules:**
- Do not publish, register names, create tags or releases, push, or add secrets.
- Prepare everything, and verify it locally with dry runs.
- Publishing waits for the author's decisions D1 (licence) and D3 (package name). As of 2026-10-06,
  `mlca` and `mlca-agent` are unregistered on both PyPI and npm. `ml-copilot-agent` on PyPI is the
  author's own v1 package (0.1.9), so v2 could also ship there as 0.2.0. Leave the name in **one** place
  (section A1) so it can be switched.

## A. The Python artefact

1. **Single sources.**
   - The version lives only in `src/mlca/__init__.py`; use hatch dynamic versioning (`[tool.hatch.version]`).
   - The distribution name lives only in `pyproject.toml`. Add `packaging/NAME` holding the chosen name;
     the npm/brew/installer generators read it.
2. **Metadata.**
   - `readme`, `license` (placeholder until D1, and refuse to build a release without one: see C),
     `authors`, `urls`, `classifiers`, `keywords`, `requires-python = ">=3.11"`.
   - Optional extras: `web = ["textual-serve"]`, `dev` stays in the dependency group.
3. **Wheel contents.**
   - Templates, styles, assets (`logo.txt`, `logo.png`, `banner.txt`; exclude `logo_source.png` from the
     wheel) and `mlca_runtime` must all be present.
   - Add `scripts/check_wheel.py`: build with `uv build`, list the wheel's files, and assert each required
     resource is present.
   - Test that a fresh `uv tool install dist/*.whl` runs `mlca --version` and `mlca doctor --json` from
     a clean temporary `HOME`.
4. **`mlca web`.** A command that serves the same Textual TUI locally in a browser via `textual-serve`
   (bind `127.0.0.1` only, print the URL). It fails with a clear message if the `web` extra is missing.
   Test with a start-and-stop smoke check.

## B. Cross-platform runtime (makes the installers honest)

Current blockers for macOS and native Windows, all in `src/mlca/runner/process.py` and `src/mlca/sandbox/`:
- `HOME="/tmp"`, `TMPDIR="/tmp"`, and `PATH` containing `/usr/bin:/bin` are hard-coded. Use
  `tempfile.gettempdir()`, a per-step temp home, and `os.pathsep`, with no POSIX directories on Windows.
- The audit-hook read roots list POSIX system directories. Build them from `sys.base_prefix`,
  `sysconfig.get_paths()` and the project environment. On Windows, compare paths case-insensitively.
- Level B is opt-in (`sandbox.allow_level_b`). Keep it opt-in.
  - `mlca doctor` must explain the level per OS and how to opt in.
  - On Windows it must recommend WSL2 for level A.

Each step must still run under level B on macOS and Windows with the audit hook active. The
vault/test-lock behaviour is identical on every OS.

**Test:** the existing integration tests parametrised over the available level. In CI, macOS and Windows
run the level-B path.

## C. Release pipeline (GitHub Actions; files only, nothing triggered)

1. **`.github/workflows/ci.yml`** on push and PR:
   - ruff, then `uv run pytest -q` on `ubuntu-latest` (level A: install `bubblewrap`), `macos-latest`
     (level B) and `windows-latest` (level B);
   - Python 3.11 and 3.13;
   - a wheel check (A3).
2. **`.github/workflows/release.yml`** on a `v*` tag **and** `workflow_dispatch`. Jobs, each needing the
   previous one:
   1. `verify`: tag equals `__version__`; licence is not the placeholder; CI suite green.
   2. `build`: `uv build`; upload `dist/` as an artefact; generate `SHA256SUMS`.
   3. `publish-pypi`: PyPI **trusted publishing** (OIDC, no token), in a GitHub `environment: release`
      that requires manual approval.
   4. `github-release`: attach the wheel, sdist, `SHA256SUMS`, `install.sh`, `install.ps1`.
   5. `publish-npm`: `npm publish --provenance` from `packaging/npm` (`NPM_TOKEN` secret, same protected
      environment).
   6. `update-homebrew`: render the formula with the new version and sha256 and open a PR to the tap repo.
      The job is skipped unless the `HOMEBREW_TAP` variable is set.
3. **`docs/releasing.md`.** The one-time setup only the author can do:
   - PyPI trusted publisher;
   - npm account/scope and token;
   - tap repository;
   - the protected environment.

   Then the release checklist.
4. **Verify locally:**
   - `actionlint`, if available (otherwise a YAML syntax check);
   - `act -n`, if available (dry run);
   - record what could not be run.

## D. Installers

### D1. `installers/install.sh` (Linux, macOS, WSL)
- POSIX `sh`, `set -eu`.
- Flags: `--version X`, `--yes` (non-interactive), `--no-modify-path`.
- Steps:
  1. Detect OS and architecture.
  2. If `uv` is missing, explain what will be installed and ask (or honour `--yes`), then run Astral's
     official installer.
  3. `uv tool install "<name>==<version>"` (latest if no version), or `uv tool upgrade` if already
     installed.
  4. On Linux without `bwrap`, print the distro-specific install line:
     - apt: `sudo apt install bubblewrap`;
     - dnf: `sudo dnf install bubblewrap`;
     - pacman: `sudo pacman -S bubblewrap`;
     - zypper: `sudo zypper install bubblewrap`.

     Never run sudo yourself.
  5. On macOS, explain level B and the opt-in line.
  6. Finish with `mlca doctor`, which prints the banner.
- No other network calls, and no telemetry.
- **Test:** `shellcheck`, if available, plus a run inside a temporary `HOME` with a fake `uv` on `PATH`
  that records its arguments.

### D2. `installers/install.ps1` (Windows)
- Same flow: Astral's PowerShell installer for uv (with consent), then `uv tool install`, then
  `mlca doctor`.
- It first prints: "For full isolation use WSL2: `wsl --install`, then run install.sh inside WSL."
- **Test:** PSScriptAnalyzer if available; otherwise a syntax parse with `pwsh -NoProfile -Command` if
  `pwsh` exists. Record what could not be run.

### D3. npm launcher, `packaging/npm/`
- **Files:** `package.json` (name from `packaging/NAME`, version synced from `__version__` by
  `scripts/sync_versions.py`, `bin: {"mlca": "bin/mlca.js"}`, `engines.node >= 18`, **no
  `postinstall`/`preinstall` scripts**), `bin/mlca.js`, `README.md`, `LICENSE` (copied at build).
- **`bin/mlca.js` behaviour:**
  1. Find `uv` on `PATH` or in Astral's default locations. If missing, print the one-line install
     command for the OS and exit 1; never download anything from the launcher.
  2. Run `uv tool run --from "<name>==<pinned version>" mlca <args>` with `stdio: "inherit"`, forwarding
     the exit code and signals. Pin the version so npm and Python versions always match.
  3. `MLCA_LAUNCHER_DEBUG=1` prints the resolved command.
- npm generates the `.cmd` shim on Windows; check that `bin/mlca.js` has no POSIX-only assumptions.
- **Test:** `node --test packaging/npm/test/` with a fake `uv` executable: argument forwarding, exit code,
  missing-uv message. Run `npm pack --dry-run` and check that the file list contains no stray files.

### D4. Homebrew, `packaging/homebrew/mlca.rb.tmpl` + `scripts/render_formula.py`
- A tap formula that `depends_on "uv"` and installs a small `mlca` wrapper script running
  `uv tool run --from "<name>==<version>" mlca "$@"`. Bundling pandas/pyarrow as Homebrew resources is
  too heavy, and the wrapper keeps one artefact.
- `brew test` block: `mlca --version`.
- The renderer fills in the version and the PyPI sdist sha256 at release time (C2.6).
- **Test:** render with a dummy sha256 and run `ruby -c`, if available.

## E. Documentation

- `docs/install.md`: one section per channel; the OS support table (Linux level A; macOS level B opt-in;
  Windows via WSL2 recommended, native level B opt-in); uninstall commands (`uv tool uninstall`,
  `npm rm -g`, `brew uninstall`); where config, keys and data live.
- Update the `README.md` install section to the three shortest commands (uv, curl, npx).
- `docs/architecture.md`: a short "Distribution" paragraph with the one-artefact, many-wrappers diagram.

## F. Done when

- `uv run pytest -q` passes, now including the wheel check, the `mlca web` smoke test, the npm launcher
  tests and the installer dry-run tests. Paste the summary line.
- `uv build` produces a wheel that installs into a clean `uv tool` environment, and `mlca doctor` runs
  there and shows the banner.
- `npm pack --dry-run` lists only the intended files.
- Workflows parse; the publishing jobs are guarded by the protected environment and the D1/D3 checks.
- `docs/DECISIONS.md` records the choices, and lists D1 and D3 as the remaining blockers for publishing.
- Local commits only (one per section A–E). Nothing published, tagged, pushed or registered.
- The final message lists:
  - what was built;
  - every check that ran, with results;
  - every check that could not run here (e.g. Windows, macOS, `act`), with the reason;
  - the exact one-time steps the author must do before the first release.
