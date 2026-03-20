# Debian Errata Publish CI Component

## Problem

Publishing Debian packages to the UCS errata repository requires manual invocation of `repo_admin.py` and `build-package-ng`, and duplicating CI configuration across repositories.

## Solution

This GitLab CI/CD component automates errata publishing. When `debian/changelog` changes on the default branch, it imports and builds the package automatically.

## Jobs Produced

| Job | Runner | Purpose |
|-----|--------|---------|
| `errata-import` | `omar` | Imports package metadata via `repo_admin.py` |
| `errata-build` | `ladda` | Builds and publishes via `build-package-ng` |

## Configuration

| Input | Default | Description |
|-------|---------|-------------|
| `debian-package` | (required) | Name of the Debian package |
| `debian-scope` | `errata${UCS_VERSION}` | Target scope (expanded at runtime) |
| `ucs-version` | `$UCS_VERSION` | Full UCS version from the base.yml (expanded at runtime) |
| `pkg-dir` | `.` | Path to the package directory (contains `debian/`) |
| `stage` | `publish` | Stage for the jobs |

## Usage

```yaml
include:
  - project: univention/dev/ucs
    file: .gitlab-ci/base.yml
  - component: $CI_SERVER_FQDN/univention/ci/debian-errata-publish@v1.0.0
    inputs:
      debian-package: my-package
      pkg-dir: src/my-package

stages: [publish]
```

The component inherits `$UCS_VERSION` from `base.yml`, so both `--release` and `--scope` are derived automatically.

## Trigger Rules

Jobs run when:

- Commit is on the default branch
- `debian/changelog` in `pkg-dir` was modified
