# MLCA launcher

This package runs the same versioned Python artifact as the other MLCA installers. Install uv first,
then use `npx mlcagent` or `npm install -g mlcagent`. The launcher never downloads uv, has no install hooks or
telemetry, preserves arguments, and delegates to `uv tool run`. Python >=3.11 is required; uv can
provision it. Set `MLCA_LAUNCHER_DEBUG=1` to print the resolved command.

The npm package is prepared locally and is not published. The author approved the name `mlcagent`
and CC-BY-NC-ND-4.0 licence. npm publication needs separate authorization. Prereleases map to npm
SemVer while `mlca.pythonVersion` pins the exact Python release. Linux needs bubblewrap for level A. macOS/native Windows require explicit level B opt-in;
Windows users can use WSL2 plus bubblewrap for level A. See the Python project's installation guide.
