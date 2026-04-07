# Debian Errata Build CI Component

## Problem

Publishing Debian packages to the UCS errata repository requires manual invocation of `repo_admin.py` and `build-package-ng`, and duplicating CI configuration across repositories. When maintaining packages for multiple UCS releases simultaneously, each release branch needs to build for the correct UCS version.

## Solution

This GitLab CI/CD component automates errata builds. When `debian/changelog` changes on a protected branch, it imports and builds the package automatically. The UCS version is read from the `$UCS_VERSION` variable defined in the consuming repo's `.gitlab-ci.yml` — bump it when starting a new release branch.

## Jobs Produced

| Job | Runner | Purpose |
|-----|--------|---------|
| `errata-import` | `omar` | Imports package metadata via `repo_admin.py` |
| `errata-build` | `ladda` | Builds and publishes via `build-package-ng` |

## Configuration

| Input | Default | Description |
|-------|---------|-------------|
| `debian-package` | (required) | Name of the Debian package |
| `debian-scope` | `errata${UCS_VERSION}` | Target scope (uses `$UCS_VERSION` at runtime) |
| `ucs-version` | `$UCS_VERSION` | Full UCS version, set in your `.gitlab-ci.yml` variables |
| `pkg-dir` | `.` | Path to the package directory (contains `debian/`) |
| `stage` | `publish` | Stage for the jobs |

## Usage

```yaml
variables:
  # Bump when starting a new UCS release branch
  UCS_VERSION: "5.2-5"

include:
  - component: $CI_SERVER_FQDN/univention/ci/debian-errata-build@v1.0.0
    inputs:
      debian-package: my-package
      pkg-dir: src/my-package

stages: [publish]
```

## Trigger Rules

Jobs run when:

- Branch is protected
- `debian/changelog` in `pkg-dir` was modified
