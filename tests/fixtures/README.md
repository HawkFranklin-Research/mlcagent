# Offline reviewer fixtures

The original table generator, brief and scripted provider were copied from `docs/prompts/fixtures/`.
`tests/conftest.py` creates the same fixed-seed 400-row table, adds a group column for the grouped-split
variant, and duration/observed columns for the survival variant. Its alternate-model response uses the
same deterministic pipeline with the alternative output filename. No metrics are scientific results.

Tests set `UV_OFFLINE=1`. Before an offline run, `uv sync --group dev` primes uv's external cache with
the analysis and build dependencies. Temporary analysis environments are real separate environments;
project fixtures clean them after each test. Scratch folders are outside the repository, on the user's
cache filesystem to avoid a limited `/tmp` mount. No credential files or original datasets are read.
