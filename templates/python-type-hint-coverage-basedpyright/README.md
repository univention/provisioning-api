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

- A ready-to-copy pre-commit hook snippet for local baseline-aware checks plus a CI pattern that
  avoids docker-in-docker. The pre commit hooks are also used to generate the initial baseline
  (or forcefully update an existing one).
- CI template that runs `uvx --python <version> basedpyright` and publishes GitLab Code Quality output.
- Supports custom environment setup through `before_script`, for example `uv sync --python 3.11`.

## Table of contents

- [python-type-hint-coverage-basedpyright](#python-type-hint-coverage-basedpyright)
  - [At a glance](#at-a-glance)
  - [Table of contents](#table-of-contents)
  - [Setup](#setup)
  - [Monorepo setup (one job per package)](#monorepo-setup-one-job-per-package)
  - [Avoid job name collisions in composed pipelines](#avoid-job-name-collisions-in-composed-pipelines)
  - [uv workspace monorepos](#uv-workspace-monorepos)
  - [Run basedpyright via pre-commit](#run-basedpyright-via-pre-commit)
  - [Avoid docker-in-docker in CI](#avoid-docker-in-docker-in-ci)
  - [Fail the pipeline on new diagnostics (strict mode)](#fail-the-pipeline-on-new-diagnostics-strict-mode)
  - [Troubleshooting](#troubleshooting)
  - [Scaling notes](#scaling-notes)
  - [Input reference](#input-reference)

## Setup

1. **Configure pre-commit hooks** (see [Run basedpyright via pre-commit](#run-basedpyright-via-pre-commit)).

2. **Create a baseline** in your repository once (commit it):

    ```sh
    prek run --hook-stage manual basedpyright-container-write-baseline --all-files
    ```

    In practice, the most reliable approach is to generate the baseline in the same environment as
    the CI job and local baseline-aware checks.

    > [!note]
    > If your CI job installs project dependencies in `before_script`, create or refresh the
    > baseline with the same dependency setup. Otherwise the baseline may suppress a different set
    > of diagnostics than the pipeline produces.
    >
    > See [Prepare the environment before analysis](#prepare-the-environment-before-analysis)

3. **Include the component** in your CI pipeline:

    ```yaml
    include:
      - component: $CI_SERVER_FQDN/components/ci-components/python-type-hint-coverage-basedpyright@main
        inputs:
          pipeline_stage: build
          python_paths: .
          python_version: "3.11"
          before_script:
            - uv sync --python 3.11
          baseline_file: basedpyright-baseline.json
    ```

    This creates a job named `type_hint_basedpyright` in the `build` stage. The job is non-blocking
    by default (`allow_failure: true`). Each run also writes `basedpyright-code-quality.json` and
    publishes it through GitLab `artifacts:reports:codequality` so merge requests can surface the
    diagnostics in the Code Quality UI.

4. Going forward, only code that introduces *new* diagnostics beyond the baseline fails the job.

5. As you fix existing errors, the baseline **shrinks automatically** when you run basedpyright
  with `--baselinemode=auto`. In local development, this is the default behavior of the
  automatic pre-commit hook `basedpyright-container-baseline`, which runs on normal pre-commit
  execution and removes baseline entries that no longer match any diagnostic.

   ```sh
   basedpyright --baselinefile basedpyright-baseline.json --baselinemode=auto
   ```

   > [!note]
   > The `basedpyright-container-baseline` hook updates or shrinks the baseline only when the run
   does not introduce any new type hint issues.

## Monorepo setup (one job per package)

For monorepos, include this component once per Python package. Use a unique `job_prefix` per
package, point `python_paths` to that package, and keep one baseline file per package.

```yaml
include:
  - component: $CI_SERVER_FQDN/components/ci-components/python-type-hint-coverage-basedpyright@main
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

  - component: $CI_SERVER_FQDN/components/ci-components/python-type-hint-coverage-basedpyright@main
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
  - component: $CI_SERVER_FQDN/univention/dev/tooling/ci-components/python-type-hint-coverage-basedpyright@main
    inputs:
      pipeline_stage: build
      python_paths: .
      python_version: "3.11"
      baseline_file: basedpyright-baseline.json
      before_script:
        - uv sync --python 3.11 --dev
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
prek run --hook-stage manual basedpyright-container-write-baseline --all-files
```

If you use `pre-commit` directly instead of `prek`, run:

```sh
pre-commit run --hook-stage manual basedpyright-container-write-baseline --all-files
```

## Run basedpyright via pre-commit

Use local hooks to keep developer feedback fast and baseline-aware.

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: basedpyright-container-baseline
        name: basedpyright (relative to baseline)
        language: docker_image
        entry: |
          gitregistry.knut.univention.de/univention/dev/tooling/ci-components/uv:latest sh -c '
          export UV_CACHE_DIR=/src/.cache/uv/cache;
          export HOME=/src/.cache/uv/home;
          export XDG_CACHE_HOME=/src/.cache/uv/xdg-cache;
          export XDG_DATA_HOME=/src/.cache/uv/xdg-data;
          mkdir -p "$UV_CACHE_DIR" "$HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME";
          uvx --python 3.11 basedpyright \
            --project pyrightconfig.json \
            --baselinefile basedpyright-baseline.json \
            --baselinemode=auto' --
        pass_filenames: false
        types: [python]

      - id: basedpyright-native-baseline
        name: basedpyright (relative to baseline, native)
        language: system
        entry: |
          sh -c 'uvx basedpyright \
            --project pyrightconfig.json \
            --baselinefile basedpyright-baseline.json \
            --baselinemode=auto' --
        stages: [manual]
        pass_filenames: false
        types: [python]

      - id: basedpyright-container-no-baseline
        name: basedpyright (lint file, no baseline)
        language: docker_image
        entry: |
          gitregistry.knut.univention.de/univention/dev/tooling/ci-components/uv:latest sh -c '
          export UV_CACHE_DIR=/src/.cache/uv/cache;
          export HOME=/src/.cache/uv/home;
          export XDG_CACHE_HOME=/src/.cache/uv/xdg-cache;
          export XDG_DATA_HOME=/src/.cache/uv/xdg-data;
          mkdir -p "$UV_CACHE_DIR" "$HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME";
          uvx --python 3.11 basedpyright \
            --project pyrightconfig.json \
            --baselinefile /tmp/nonexistent-basedpyright-baseline.json' --
        stages: [manual]
        pass_filenames: true
        types: [python]

      - id: basedpyright-container-write-baseline
        name: basedpyright (write baseline)
        language: docker_image
        entry: |
          gitregistry.knut.univention.de/univention/dev/tooling/ci-components/uv:latest sh -c '
          export UV_CACHE_DIR=/src/.cache/uv/cache;
          export HOME=/src/.cache/uv/home;
          export XDG_CACHE_HOME=/src/.cache/uv/xdg-cache;
          export XDG_DATA_HOME=/src/.cache/uv/xdg-data;
          mkdir -p "$UV_CACHE_DIR" "$HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME";
          uvx --python 3.11 basedpyright \
            --project pyrightconfig.json \
            --baselinefile basedpyright-baseline.json \
            --writebaseline .' --
        stages: [manual]
        pass_filenames: false
```

Concept of these hooks:

- `basedpyright-container-baseline` (default): local baseline-aware check. With `--baselinemode=auto`, the baseline shrinks as existing issues are fixed and no new issues are introduced.
  > [!note]
  > Because this pre-commit hook runs by default, your CI pipeline can fail when it verifies pre-commit hooks in a containerized runner. See [Avoid docker-in-docker in CI](#avoid-docker-in-docker-in-ci).
- `basedpyright-native-baseline` (manual): baseline-aware check without docker-in-docker, useful in CI runners that already execute inside a container.
- `basedpyright-container-no-baseline` (manual): full type-check output without baseline suppression.
- `basedpyright-container-write-baseline` (manual): create or force-refresh the baseline file.

Keep the Python version aligned across:

- this component's `python_version` input
- `before_script` commands such as `uv sync --python 3.11`
- local hook commands such as `uvx --python 3.11 basedpyright`

Optional `pyrightconfig.json`:

```json
{
  "venvPath": ".",
  "pythonVersion": "3.11"
}
```

If you prefer, pass the Python version directly in hook commands via `--pythonversion 3.11`.
Keep it aligned with your CI `python_version` input.

Run manual hooks:

```sh
# prek
prek run --hook-stage manual basedpyright-container-write-baseline --all-files
prek run --hook-stage manual basedpyright-container-no-baseline --all-files

# pre-commit
pre-commit run --hook-stage manual basedpyright-container-write-baseline --all-files
pre-commit run --hook-stage manual basedpyright-container-no-baseline --all-files
```

## Avoid docker-in-docker in CI

When your pipeline already runs inside a container, a default `docker_image` pre-commit hook can
fail because it tries to start another container runtime. The intended pattern is:

1. Run the container-based hook by default on developer machines.
2. Mark the native hook as `stages: [manual]`.
3. In CI, skip the container hook and explicitly run the native manual hook.

Example with the `pre-commit` component:

```yaml
include:
  - component: $CI_SERVER_FQDN/univention/dev/tooling/ci-components/pre-commit@main
    inputs:
      skip_hooks: "basedpyright-container-baseline"
      manual_stage_hooks: "basedpyright-native-baseline"
```

This keeps local developer UX unchanged while CI runners execute basedpyright directly inside the
job container instead of requiring docker-in-docker.

## Fail the pipeline on new diagnostics (strict mode)

```yaml
inputs:
  allow_failure: false
```

## Troubleshooting

- `Configured python_paths entry not found`: verify `python_paths` is correct relative to repo root.
- `Configured baseline_file not found`: commit the package baseline JSON file and verify the path.
- `uv sync` or dependency setup is slow on repeated pipelines: keep installs in `.venv/` or another workspace-local path so the runner can reuse the component cache.
- GitLab Code Quality widget is empty: download `basedpyright-code-quality.json` from the job artifacts and confirm the run had in-scope diagnostics or an empty JSON array after baseline suppression.
- Job name collision in pipeline: use unique `job_prefix` for each include.
- Too many monorepo jobs run on each MR: narrow `job_rules` with package-specific `changes`.
- Package job did not run after shared-code/config change: include shared paths and root typing
  config files in each package's `changes` list.
- Pre-commit basedpyright hook fails in CI because Docker is unavailable: configure the `pre-commit` component with `skip_hooks: "basedpyright-container-baseline"` and `manual_stage_hooks: "basedpyright-native-baseline"`.

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
| `uv_image` | `gitregistry.knut.univention.de/univention/dev/tooling/ci-components/uv:latest` | Image providing `uv` and `uvx` for the job. |
| `python_version` | `3.13` | Python version target passed to basedpyright. |
| `python_paths` | `.` | Space-separated list of files or directories to analyze. |
| `baseline_file` | `basedpyright-baseline.json` | Path to the committed baseline file passed to `basedpyright --baselinefile`. |
| `before_script` | `echo "Tip: Specify with before_script setup steps like uv sync"` | Commands run before basedpyright, for example `uv sync --python 3.11 --dev`. |
| `allow_failure` | `true` | Set to `false` to block the pipeline on new diagnostics. |
