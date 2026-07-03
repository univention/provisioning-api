# ucsschool ci utils

This repository contains gitlab CI components that are used by some of the repositories of the UCS@school team.

## app-release

The `app-release` component is documented in [templates/app-release/README.md](templates/app-release/README.md).

## ai-review

The `ai-review` component adds a manual AI code review job to merge request pipelines.
It is documented in [templates/ai-review/README.md](templates/ai-review/README.md).

## Local CI Verification

Quick commands to validate pipeline before pushing.

### Quick Start

**Validate syntax (GitLab-facing):**

```bash
glab ci lint
```

**List available jobs:**

```bash
npx gitlab-ci-local --list --file .gitlab-ci.yml
```

If your jobs use `rules:` with CI variables, list with explicit context:

```bash
npx gitlab-ci-local --list --file .gitlab-ci.yml \
  --variable CI_PIPELINE_SOURCE=merge_request_event \
  --variable CI_COMMIT_BRANCH=$CI_DEFAULT_BRANCH \
  --ignore-predefined-vars CI_PIPELINE_SOURCE,CI_COMMIT_BRANCH
```

**Run a specific job:**

```bash
npx gitlab-ci-local <job_name> --file .gitlab-ci.yml --cleanup
```

**Validate dependency chain:**

```bash
npx gitlab-ci-local --validate-dependency-chain --file .gitlab-ci.yml
```

### Setup

- **glab:** See [github.com/profclems/glab](https://github.com/profclems/glab)
- **gitlab-ci-local:** See [github.com/firecow/gitlab-ci-local](https://github.com/firecow/gitlab-ci-local)
- **PAT scope:** `glab` requires full `api` scope on your Personal Access Token

### Type-Hint Coverage Fixtures

```bash
npx gitlab-ci-local validate_basedpyright_type_hint_coverage \
  --needs \
  --file .gitlab-ci.yml \
  --variable CI_PIPELINE_SOURCE=merge_request_event \
  --cleanup
```
