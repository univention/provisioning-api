# Debian Branch Build CI Component

## Problem

Testing Debian package changes before release requires either manual builds or duplicating CI configuration across repositories. Test VMs need a way to install branch versions without manual package copying.

## Solution

This GitLab CI/CD component creates **per-branch Aptly repositories** automatically. Every push to a non-protected branch builds the package and publishes it to a branch-specific apt repository.

Test VMs can install branch packages by adding a single apt source:

```bash
echo "deb [trusted=yes] http://omar.knut.univention.de/build2/git/<project> <branch-slug> main" \
  > /etc/apt/sources.list.d/branch.list
apt-get update && apt-get install <package>
```

## Why This Approach

- **Pre-release versioning**: Branch builds use `A~` suffixes that sort *below* release versions. When the real release lands, apt upgrades automatically - no cleanup needed.
- **Build-dep chaining**: The branch repo is added as a build source, so multi-package repos can build interdependent packages in sequence.
- **Auto-cleanup**: Branch environments expire after 6 months (configurable), removing stale repos.

## Jobs Produced

| Job | Purpose |
|-----|---------|
| `prepare-aptly` | Creates the Aptly repo and publishes it (idempotent). Registers a GitLab environment with auto-stop. |
| `aptly-remove` | Deletes the repo on environment stop (manual trigger). |
| `build-deb` | Builds the package and uploads to Aptly. Works out of the box for single-package repos. |
| `.build-deb` | Hidden template for multi-package repos to `extends:` from. |

## Configuration

| Input | Default | Description |
|-------|---------|-------------|
| `pkg-dir` | `.` | Path to the package directory (must contain `debian/`) |
| `deb-image` | `ucs-base-flex-525:latest` | Container image for builds (must have dpkg-buildpackage) |
| `ucs-version` | `$UCS_VERSION` | Full UCS version for errata repos and version stamps (expanded via `expand_vars`) |
| `aptly-api` | `http://omar.knut.univention.de:11620/api` | Aptly REST API endpoint |
| `apt-url` | `http://omar.knut.univention.de/build2/git` | Public URL where Aptly serves packages |
| `stage-prepare` | `prepare` | Stage for the prepare job |
| `stage-build` | `build` | Stage for the build job |
| `stage-cleanup` | `.post` | Stage for the cleanup job |
| `auto-stop-in` | `6 months` | Time before the branch environment auto-stops and the repo is deleted |

## Usage

### Single-Package Repo

The component uses `$UCS_VERSION` from the UCS repository by default. Include `base.yml` to define this variable:

```yaml
include:
  - project: univention/dev/ucs
    file: .gitlab-ci/base.yml
  - component: $CI_SERVER_FQDN/univention/ci/deb-branch-build@1

stages: [prepare, build, .post]
```

### With Custom Settings

```yaml
include:
  - project: univention/dev/ucs
    file: .gitlab-ci/base.yml
  - component: $CI_SERVER_FQDN/univention/ci/deb-branch-build@1
    inputs:
      pkg-dir: src/my-package
      auto-stop-in: "2 weeks"

stages: [prepare, build, .post]
```

To override the UCS version, pass a literal value:

```yaml
include:
  - component: $CI_SERVER_FQDN/univention/ci/deb-branch-build@1
    inputs:
      ucs-version: "5.0-10"
```

### Multi-Package Repo

Extend `.build-deb` for additional packages:

```yaml
include:
  - project: univention/dev/ucs
    file: .gitlab-ci/base.yml
  - component: $CI_SERVER_FQDN/univention/ci/deb-branch-build@1

stages: [prepare, build, .post]

# Override the default job for the first package
build-deb:
  variables:
    PKG_DIR: packages/core

# Additional packages
build-extensions:
  extends: .build-deb
  variables:
    PKG_DIR: packages/extensions
  needs:
    - prepare-aptly
    - build-deb  # if extensions depends on core
```

## Local Testing

A docker-compose setup is provided for testing the pipeline locally:

```bash
docker compose run --rm aptly-prepare
docker compose run --rm aptly-build
docker compose run --rm aptly-remove
```
