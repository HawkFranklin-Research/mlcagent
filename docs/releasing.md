# Release preparation and author setup

D1 is resolved as CC-BY-NC-ND-4.0 and D3 as `mlca`. The author authorized one manual PyPI
upload of 0.2.0b1. This does not authorize GitHub pushes, npm publication or a new remote.
The GitHub release pipeline remains unconfigured; the steps below describe future setup.
See [implementation status](IMPLEMENTATION_STATUS.md) for the actual publication result.

## One-time author steps

1. D1 is resolved: the official CC-BY-NC-ND-4.0 legal code is in `LICENSE`; Python metadata uses
   the SPDX expression and `license-files`. Keep licence mirrors synchronized.
2. D3 is resolved as `mlca`. Maintain the shared unscoped Python/npm name in `pyproject.toml` (`project.name`). The version lives
   only in `src/mlca/__init__.py`. Run `uv run python scripts/sync_versions.py` to refresh NAME, installers
   and npm identity/licence. `packaging/NAME` and package.json are generated mirrors, not edit points.
3. Choose/create the v2 GitHub repository and update the public metadata URLs and contributor list.
   Connecting/pushing this checkout is a separate author action. Source metadata currently labels the
   existing v1 URL explicitly as the legacy implementation.
4. In GitHub settings create environment **release** with required human reviewers. Require approval
   for deployment and restrict releases to version tags. Configure the repository variable
   `PACKAGE_NAME_APPROVED` to the exact chosen distribution name. A tag must equal `v<__version__>`.
5. In PyPI configure a trusted publisher with this GitHub owner/repository, workflow `release.yml`
   and environment `release`. That future workflow uses trusted publishing rather than an API
   token; the separately authorized initial manual beta upload uses an environment-only token.
6. Configure the npm account/name (and organisation if relevant). Add a publishing token as the
   protected release environment's `NPM_TOKEN`; the workflow exposes it only as NODE_AUTH_TOKEN to
   `npm publish --provenance`. Do not put it in source, docs, installer files or .npmrc.
7. Optional Homebrew: create a tap repository with a Formula directory, set repository variable
   `HOMEBREW_TAP=owner/tap`, and set protected secret `HOMEBREW_TAP_TOKEN` with permission to push an
   update branch and open a PR in that tap. Without HOMEBREW_TAP, this job is skipped.

Environment protection is an external GitHub setting: YAML names an environment but cannot create
its required reviewers. Verify that setting before enabling any publication. No local action here
changed those settings or stored secrets.

## Release checklist

- Review the scientific DRAFT templates and supported OS claims; original-data and live-provider
  validation remain separate from the synthetic harness suite.
- Update the single version source and run sync_versions.py. Keep generated files committed.
- Run `uv sync --locked --group dev`, dependency-cache priming, `uv run pytest -q`, lint/format,
  `uv run python scripts/check_wheel.py`, Node launcher tests and `npm pack --dry-run`.
- With D1/D3 resolved, run `uv run python scripts/verify_release.py --tag v<VERSION>
  --approved-name <NAME>`. The author-approved beta tag is `v0.2.0b1`.
- Confirm the six-job OS/Python CI matrix is green. Native Windows/macOS results cannot be inferred
  from Linux level-B tests. Linux CI uses bubblewrap; its ephemeral runner enables user namespaces
  if AppArmor restricts them, without changing developer machines.
- The author may then create/push a matching version tag, or dispatch release.yml **on that tag**.
  Dispatching from a branch fails the version/tag check. Do not trigger it during local preparation.
- The workflow runs CI, verifies decisions/tag, builds wheel/sdist plus SHA256SUMS, and then waits for
  protected release approval. PyPI publish → GitHub release assets → npm publish → optional tap PR.
  Each publication job needs the previous one. Approvals and publishing are author actions.
- After publication, update `<release-base-url>`/`<tap>` in the install guide and validate installs on
  clean supported machines. A prepared dry-run installer is not evidence of a published channel.

## Local results and unavailable tools

See [implementation status](IMPLEMENTATION_STATUS.md) for the exact final suite count and tool results.
Here, shell syntax, fake-uv installer/launcher runs, npm file listing, Ruby syntax, wheel installation,
loopback HTTP smoke, release guards and workflow YAML parsing can run. shellcheck, pwsh,
PSScriptAnalyzer, actionlint and act are absent. Actual Homebrew installation and native macOS/Windows
execution require their corresponding environments. No publishing workflow was run here.

Implementation references: the browser adapter follows the documented
[Textual Serve Server API](https://github.com/Textualize/textual-serve#configuration); CI uses
[Astral's uv integration](https://docs.astral.sh/uv/guides/integration/github/). These libraries provide
transport/install plumbing; MLCA's workflow engine remains its own Python implementation.
