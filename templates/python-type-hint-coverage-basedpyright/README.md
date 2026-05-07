# python-type-hint-coverage-basedpyright

Reusable GitLab CI component that runs [basedpyright](https://github.com/DetachHead/basedpyright)
with its **baseline** feature. A committed baseline file suppresses all pre-existing errors so
only new diagnostics introduced after the baseline was created fail the job.

This lets teams adopt strict type checking incrementally without having to fix the entire
codebase first.

> **Note:** We run basedpyright in a container today so we can use baseline files,
> but we plan to migrate to [`ty`](https://github.com/astral-sh/ty) once baseline
> support is available (see [astral-sh/ty#1074](https://github.com/astral-sh/ty/issues/1074)).
> That migration should reduce complexity and improve type-checking speed.

## At a glance

- CI template with monorepo support and guidance for `uv` workspace-style dependency installation.
- A ready-to-copy pre-commit hook snippet for running baseline-aware and full type checks locally to help improve type-hint coverage.

## Table of contents

- [python-type-hint-coverage-basedpyright](#python-type-hint-coverage-basedpyright)
  - [At a glance](#at-a-glance)
  - [Table of contents](#table-of-contents)
  - [Quick start](#quick-start)
  - [Install project dependencies before analysis](#install-project-dependencies-before-analysis)
  - [Workflow](#workflow)
  - [Monorepo setup (one job per package)](#monorepo-setup-one-job-per-package)
  - [Avoid job name collisions in composed pipelines](#avoid-job-name-collisions-in-composed-pipelines)
  - [uv workspace monorepos](#uv-workspace-monorepos)
  - [Run basedpyright via prek/pre-commit](#run-basedpyright-via-prekpre-commit)
  - [Fail the pipeline on new diagnostics (strict mode)](#fail-the-pipeline-on-new-diagnostics-strict-mode)
  - [Troubleshooting](#troubleshooting)
  - [Scaling notes](#scaling-notes)
  - [Input reference](#input-reference)

## Quick start

```yaml
include:
  - component: $CI_SERVER_FQDN/components/ci-components/python-type-hint-coverage-basedpyright@~latest
    inputs:
      pipeline_stage: test
      python_paths: src
```

This creates a job named `type_hint_basedpyright` in the `test` stage. The job is non-blocking
by default (`allow_failure: true`). Each run also writes `basedpyright-code-quality.json` and
publishes it through GitLab `artifacts:reports:codequality` so merge requests can surface the
diagnostics in the Code Quality UI.

## Install project dependencies before analysis

If imports are unresolved in the container environment, install dependencies in the job before
running basedpyright. Prefer workspace-local installs, for example `.venv/`, so the runner can
cache them between jobs instead of repeatedly writing container-global state.

```yaml
inputs:
  dependency_install_command: "uv sync --dev"
```

This command runs inside the configured `basedpyright_image` and should match your project setup.
The component caches `.cache/pip/`, `.cache/uv/`, `.cache/xdg/`, and `.venv/` by default.

When this input is used, baseline generation should use the same environment too. If possible, run
the baseline command inside the same container image after executing the same dependency install
command so CI and baseline diagnostics stay aligned.

For `uv`, prefer a project-local environment such as the default `.venv/` created by `uv sync`.
For `pip`, prefer an explicit virtual environment instead of installing into container-global
site-packages.

Example:

```sh
docker run --rm \
  -v "$PWD":/src \
  gitregistry.knut.univention.de/univention/dev/tooling/ci-components/basedpyright:latest \
  sh -ceu '
    uv sync --dev && \
    basedpyright \
      --pythonversion 3.13 \
      --writebaseline \
      --baselinefile basedpyright-baseline.json \
      .
  '
```

Adjust the image, install command, Python version, baseline path, and analysis path to match your
CI inputs. Run the command from repository root so `pyproject.toml`, optional typing config files,
and relative baseline paths resolve the same way as in CI.

## Workflow

1. **Create a baseline** in your repository once (commit it):

    ```sh
    basedpyright --writebaseline --baselinefile basedpyright-baseline.json
    ```

    In practice, the most reliable approach is to generate the baseline in the same environment as
    the CI job, ideally using the same container image and dependency installation command.

    > [!note]
    > If your CI job installs project dependencies before running basedpyright, create or refresh the
    > baseline with the same dependency setup. Otherwise the baseline may suppress a different set of
    > diagnostics than the pipeline produces.
    >
    > See [Install project dependencies before analysis](#install-project-dependencies-before-analysis)

2. **Include the component** in your CI pipeline (see below).

3. Going forward, only code that introduces *new* diagnostics beyond the baseline fails the job.

4. As you fix existing errors, the baseline **shrinks automatically** when you run with
   `--baselinemode=auto`: basedpyright removes entries that no longer match any diagnostic.

    ```sh
    basedpyright --baselinefile basedpyright-baseline.json --baselinemode=auto
    ```

    This is the same mode used by the pre-commit hook. If you use `dependency_install_command`,
    run this with the same dependency setup so the environment matches CI.

## Monorepo setup (one job per package)

For monorepos, include this component once per Python package. Use a unique `job_prefix` per
package, point `python_paths` to that package, and keep one baseline file per package.

```yaml
include:
  - component: $CI_SERVER_FQDN/components/ci-components/python-type-hint-coverage-basedpyright@~latest
    inputs:
      job_prefix: "pkg_a_"
      pipeline_stage: test
      python_paths: packages/pkg_a/src
      baseline_file: packages/pkg_a/basedpyright-baseline.json
      job_rules:
        - if: $CI_MERGE_REQUEST_ID
          changes:
            - packages/pkg_a/**/*
            - packages/pkg_a/basedpyright-baseline.json
            - pyproject.toml
            - packages/shared/**/*
        - if: $CI_COMMIT_REF_PROTECTED == "true"
        - if: $CI_COMMIT_TAG

  - component: $CI_SERVER_FQDN/components/ci-components/python-type-hint-coverage-basedpyright@~latest
    inputs:
      job_prefix: "pkg_b_"
      pipeline_stage: test
      python_paths: packages/pkg_b/src
      baseline_file: packages/pkg_b/basedpyright-baseline.json
      job_rules:
        - if: $CI_MERGE_REQUEST_ID
          changes:
            - packages/pkg_b/**/*
            - packages/pkg_b/basedpyright-baseline.json
            - pyproject.toml
            - packages/shared/**/*
        - if: $CI_COMMIT_REF_PROTECTED == "true"
        - if: $CI_COMMIT_TAG
```

This produces separate jobs (`pkg_a_type_hint_basedpyright`, `pkg_b_type_hint_basedpyright`) so
failures are isolated and easy to triage in pipeline UI.

## Avoid job name collisions in composed pipelines

```yaml
inputs:
  job_prefix: "myapp_"
```

Produces the job name `myapp_type_hint_basedpyright`.

For monorepos, make prefixes stable and package-specific (for example `pkg_a_`, `pkg_b_`).

## uv workspace monorepos

In a [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/), a single `uv.lock` at the
root pins dependencies for all members. Analyse the whole workspace in one job with a single shared
baseline file:

```text
pyproject.toml              # workspace root — declares [tool.uv.workspace] members
uv.lock                     # single lock file shared by all members
basedpyright-baseline.json  # one shared baseline for the entire workspace
packages/
  pkg_a/
    pyproject.toml
    src/
  pkg_b/
    pyproject.toml
    src/
```

Use `uv sync --dev` to install all workspace members and include `uv.lock` in `changes` so the
job re-runs whenever workspace-wide dependencies are updated:

```yaml
include:
  - component: $CI_SERVER_FQDN/univention/dev/tooling/ci-components/python-type-hint-coverage-basedpyright@jgietzel/type_hint_basedpyright
    inputs:
      pipeline_stage: test
      python_paths: .
      baseline_file: basedpyright-baseline.json
      dependency_install_command: "uv sync --dev"
      job_rules:
        - if: $CI_MERGE_REQUEST_ID
          changes:
            - "**/*.py"
            - pyproject.toml
            - uv.lock
            - basedpyright-baseline.json
        - if: $CI_COMMIT_REF_PROTECTED == "true"
        - if: $CI_COMMIT_TAG
```

To create or refresh the shared baseline, run from repository root:

```sh
docker run --rm \
  -v "$PWD":/src \
  gitregistry.knut.univention.de/univention/dev/tooling/ci-components/basedpyright:branch-jgietzel-typehintbasedpyright \
  sh -ceu '
    uv sync --dev && \
    basedpyright \
      --pythonversion 3.13 \
      --writebaseline \
      --baselinefile basedpyright-baseline.json \
      .
  '
```

Adjust `3.13` if you override `python_version`.

## Run basedpyright via prek/pre-commit

Use local containerized pre-commit hooks so developers can run both checks locally:
- baseline-aware check (default)
- full check without baseline (manual trigger)

Because the basedpyright image already contains a pinned basedpyright installation, this avoids
re-downloading `basedpyright` and `nodejs-wheel-binaries` on every `prek` run.

> [!note]
> The baseline-aware hook `basedpyright-baseline` uses `--baselinemode=auto`, which applies
> baseline shrinking as existing type-hint diagnostics are fixed.
> In practice, `basedpyright-baseline.json` is updated only when a run introduces no new
> type-hint diagnostics and existing baseline entries can be removed.

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: basedpyright-baseline
        name: basedpyright (relative to baseline)
        language: docker_image
        entry: "gitregistry.knut.univention.de/univention/dev/tooling/ci-components/basedpyright:latest sh -c 'basedpyright --pythonversion 3.13 --baselinefile basedpyright-baseline.json --baselinemode=auto \"$@\"' --"
        types: [python]

      - id: basedpyright
        name: basedpyright
        language: docker_image
        entry: "gitregistry.knut.univention.de/univention/dev/tooling/ci-components/basedpyright:latest sh -c 'basedpyright --pythonversion 3.13 --baselinefile /tmp/nonexistent-basedpyright-baseline.json \"$@\"' --"
        stages: [manual]
        types: [python]
```

Run the baseline-aware hook in normal pre-commit runs. Trigger the non-baseline hook manually when needed:

```sh
prek run --hook-stage manual basedpyright --all-files
```

Keep `--pythonversion` aligned with your CI input (`python_version`) so local and CI diagnostics stay consistent.
Run the hook from repository root so config and baseline discovery match CI behavior.

> [!tip]
> If your project installs dependencies into a local virtual environment (for example `.venv/`),
> add a `pyrightconfig.json` at repository root so local runs resolve imports consistently.
> This is optional, but it helps keep local diagnostics aligned with CI.

```json
{
  "venvPath": ".",
  "venv": ".venv"
}
```

## Fail the pipeline on new diagnostics (strict mode)

```yaml
inputs:
  allow_failure: false
```

## Troubleshooting

- `Configured python_paths entry not found`: verify `python_paths` is correct relative to repo root.
- `Configured baseline_file not found`: commit the package baseline JSON file and verify the path.
- Dependency installs are slow on repeated pipelines: keep installs in `.venv/` or another workspace-local path so the runner can reuse the component cache.
- GitLab Code Quality widget is empty: download `basedpyright-code-quality.json` from the job artifacts and confirm the run had in-scope diagnostics or an empty JSON array after baseline suppression.
- Job name collision in pipeline: use unique `job_prefix` for each include.
- Too many monorepo jobs run on each MR: narrow `job_rules` with package-specific `changes`.
- Package job did not run after shared-code/config change: include shared paths and root typing
  config files in each package's `changes` list.

## Scaling notes

- Start with one job per package for clear ownership and CI visibility.
- Use package-level `changes` filters to keep MR pipelines fast.
- For very large monorepos, prioritize critical packages as blocking (`allow_failure: false`) and
  roll out strictness package by package.
- The quick-start leaves protected-branch/tag rules broad for full coverage; scope those rules with
  `changes` too if you need lower CI fan-out on protected refs.

## Input reference

| Input | Default | Description |
| ----- | ------- | ----------- |
| `job_prefix` | `""` | Optional prefix to avoid job name collisions. |
| `pipeline_stage` | `build` | Stage for the basedpyright job. |
| `job_rules` | MR + protected branch + tag | Override to narrow execution scope. |
| `basedpyright_image` | `gitregistry.knut.univention.de/univention/dev/tooling/ci-components/basedpyright:latest` | Image to run basedpyright in. |
| `python_version` | `3.13` | Python version target passed to basedpyright. |
| `python_paths` | `.` | Space-separated list of files or directories to analyze. |
| `baseline_file` | `basedpyright-baseline.json` | Path to the committed baseline file passed to `basedpyright --baselinefile`. |
| `dependency_install_command` | `""` | Optional shell command executed before basedpyright to install project dependencies, preferably into workspace-local paths such as `.venv/`. |
| `allow_failure` | `true` | Set to `false` to block the pipeline on new diagnostics. |
