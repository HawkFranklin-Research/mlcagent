# Offline validation

Prepare dependencies once (these commands download packages but never call models):

```sh
uv sync --group dev
uv run python scripts/prime_test_cache.py
```

Then the permanent suite runs offline, including real analysis environments and slow tests:

```sh
uv run pytest -q
```

Tests set `UV_OFFLINE=1` for all uv subprocesses and use only the scripted fake provider. No API keys
or original study data are required. Cache priming also resolves optional survival dependency metadata;
installing the tool's locked dependencies alone does not always populate uv's standalone resolver cache.
The test scratch root and uv/Ruff caches belong outside the repository. Projects are cleaned after
each test. An externally supplied pytest `--basetemp` is honored.

Linux runs both level A and opted-in level B paths; level A tests skip only when bubblewrap is absent.
The namespace probe exercises private-path and network denial. macOS and native Windows run the
opted-in level B path. This is weaker isolation, not evidence of protection against malicious native code.

The suite covers required-output alternatives, primary/supporting template validation, branch checks,
column resolution and legacy compatibility, lazy sessions, incremental reads and full verification,
5,000 appends within 30 seconds, scientific fit refusals, test lock lifecycle, reports, request ledgers,
full standalone-script replay and headless TUI behavior. Synthetic metrics are harness test evidence.
