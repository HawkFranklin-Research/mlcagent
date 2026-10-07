# Installation channels

The author-approved Python package name is `mlca`; the beta is `0.2.0b1`. npm, shell download
and Homebrew channels remain unpublished. Replace
`<release-base-url>` and `<tap>` only after the author chooses the public repository and publishes.
All channels delegate to the same versioned Python wheel/source distribution; they need uv and
Python >=3.11. uv can provision a compatible Python interpreter.

| OS | Execution | Requirement |
|---|---|---|
| Linux | Level A | bubblewrap with working user namespaces; doctor reports capability until execution confirms it |
| macOS | Level B | explicit `sandbox.allow_level_b: true`; trusted generated code only |
| Windows via WSL2 | Level A recommended | `wsl --install`, then Linux uv/MLCA and bubblewrap inside WSL |
| Native Windows | Level B | explicit opt-in; native execution is covered by the prepared CI matrix, not yet verified on this host |

## Python / PyPI

```sh
uv tool install mlca==0.2.0b1
# or
pipx install mlca==0.2.0b1
```

`pipx` users also need uv available on PATH for MLCA's separate analysis environments. To try this
local checkout, run `uv build`, then `uv tool install dist/mlca-*.whl` (select one wheel).
For the browser view: `uv tool install 'mlca[web]==0.2.0b1' --reinstall`, then `mlca web`.

## Shell installer: Linux, macOS, WSL

```sh
curl -LsSf <release-base-url>/install.sh | sh
```

The installer asks before bootstrapping uv from Astral. When downloaded to a file, use
`sh install.sh --yes --version 0.2.0b1 --no-modify-path` for a pinned non-interactive installation without
shell profile changes. Beta installer files default to their explicit beta pin; stable installer files install or upgrade the latest stable release. On Linux it prints
the appropriate bubblewrap package command; it never runs sudo. On macOS it explains level B.

## PowerShell: native Windows

```powershell
irm <release-base-url>/install.ps1 | iex
```

For flags, download the script, then run `./install.ps1 -Yes -Version 0.2.0b1 -NoModifyPath`.
It recommends WSL2, asks before Astral bootstrap, installs the Python artifact and runs doctor.

## npm

```sh
npx mlca
# persistent launcher
npm install -g mlca
```

Install uv first. Node >=18 is required. The package has no install hooks; its launcher never downloads
uv and pins the Python version via `mlca.pythonVersion`; npm prereleases use their own SemVer spelling. Arguments and exit codes/signals are forwarded.
`MLCA_LAUNCHER_DEBUG=1` prints the selected command. It does not add a second agent runtime.

## Homebrew

```sh
brew install <tap>/mlca
```

The tap formula depends on uv and installs only a pinned launcher. Python/ML dependencies remain in
uv's tool and project environments. The formula template requires a release sdist SHA256; the local
render is a preview for the unpublished artifact, not a usable public tap.

## Configuration, data and removal

- Configuration: `$XDG_CONFIG_HOME/mlca/config.yaml`, or `~/.config/mlca/config.yaml` by default.
  API credentials are values in environment variables named by configuration; never save their values
  in a project or installer.
- Project state: `<project>/.mlca/`; original data files remain at their registered locations.
- Test-lock keys: `$XDG_DATA_HOME/mlca/keys/`, or `~/.local/share/mlca/keys/`. They are outside projects.
  Preserve these when keeping encrypted study evidence. Installers do not inspect or delete them.
- Uninstall Python tool: `uv tool uninstall mlca` (or `pipx uninstall mlca`).
- Remove npm wrapper: `npm rm -g mlca`; a Python tool installed separately needs its own removal.
- Remove Homebrew wrapper: `brew uninstall mlca`.

Run `mlca doctor` in a terminal for the logo, environment status and OS-specific isolation guidance.
The `--json` form omits the banner for scripts. Tests are described in [testing](testing.md).
