# TODO — CI App Center release automation for provisioning (v1: keycloak parity)

Goal: implement the same tagged-release + CI App Center release automation as the
keycloak repo (commits `dd2ce35..1a65c7f`). Manual protected `vX.Y.Z` /
`vX.Y.Z-nubusN` tags drive ALL releases (images, charts, App Center);
semantic-release-driven auto-releases are replaced by `.tagged-release`.
First release: **v2.2.0** (must exceed current app version 2.1).

**Implementation status (2026-07-12):** sections 2–5 are implemented in the
working tree (`.gitlab-ci.yml`, `appcenter/`, `docs/ucs/README.md`) — not yet
committed (git metadata was read-only in this session). Jinja templates were
render-tested locally (release + dev mode, UCR `@!@` blocks preserved,
backup2master inlined into inst). Remaining: section 1 verifications (need
GitLab/Provider-Portal access), CI lint against the real GitLab, section 6
rollout, and the unchecked items below.

References:
- keycloak: `.gitlab-ci.yml`, `appcenter/*.jinja`, `docs/devel/README-testing-release.md`
- ci-components: `univention/dev/tooling/ci-components/app-release@2.5.2`
- common-ci: `templates/tagged-release.yaml` (needs ref ≥ v1.64.0, keycloak uses that)
- current manual process: `docs/ucs/README.md`, `apps/push_config_to_appcenter`

## 0. Design (decided)

- Manual annotated protected tag `vX.Y.Z` on main → tag pipeline: builds all
  images (digest artifacts), publishes images + charts publicly
  (`PUBLIC_RELEASE=true`), creates App Center version `X.Y.Z`, uploads files,
  manual `do_release` gate → production App Center → `check_release` →
  GitLab release + announcement mail.
- Re-release of the same version: `vX.Y.Z-nubusN` tag.
- Main branch → dev builds only (`X.Y.Z-post-main-*` to `nubus-dev`) + keeps
  `999.0.0-staging` App Center version updated.
- MR → images on change only; App Center test version `0.0.0-<slug>` via
  *manual* `create_app_version` job, auto-expires after 3 days.
- **Consequences of dropping semantic-release (accepted):**
  - No more auto-release per merge; k8s image/chart releases happen on tag.
    Downstream (ums-stack renovate) sees new chart versions only when we tag.
  - No auto-generated CHANGELOG.md / GitLab releases from semantic-release;
    GitLab releases now come from the component's `create_gitlab_release` on
    tags. Changelog maintenance becomes manual (like keycloak's changelog.rst).
- Deferred to later iterations (see "Later / future"): semantic-release
  creating the tags, backend app automation.

## 1. Preparation / verification (small, do first)

- [ ] Confirm App Center credentials work for this project
  (`univention-appcenter-control` account for `provisioning-service`; `omar`
  runner tag for `do_release`/`send_mail`). Compare CI variables with the
  keycloak project/group.
- [ ] Confirm App Center version ordering accepts `2.1` → `2.2.0` and treats
  `2.2.0-nubus1` as newer than `2.2.0` (keycloak precedent).
- [ ] Read common-ci `templates/tagged-release.yaml` (v1.64.0+) semantics:
  `INITIAL_VERSION`, `RELEASE_TAG_PATTERN`, how dev versions are derived from
  the latest matching tag (existing `v0.70.x` tags match the pattern — verify
  dev versions and `PUBLIC_RELEASE` behave sanely before the first `v2.2.0`).
- [ ] Check common-ci changes `v1.61.2` → `v1.64.0`+ for breaking changes in
  the jobs we keep (container-build-external, helm, lint, sonarqube, pip).
- [ ] Check `build-and-publish-pip` (nubus-provisioning-common/-consumer):
  where does its package version come from today (`RELEASE_VERSION`?), and
  what changes when releases become tag-driven.
- [ ] GitLab settings: protect `v*` tags (release pipeline requires
  `CI_COMMIT_REF_PROTECTED == "true"`); who may create protected tags.

## 2. Versioning switch: semantic-release → tagged-release

- [x] Bump common-ci include `ref: v1.61.2` → keycloak's `v1.64.0` (or newer).
- [x] Drop `jobs/semantic-release-env.yaml` include; add
  `templates/tagged-release.yaml`.
- [x] Define `pre-semantic-release: extends: .tagged-release` (keep the job
  name — all downstream `needs` in common-ci jobs stay valid; keycloak does
  the same) with:
  - `INITIAL_VERSION: "2.1.0"` (floor at the shipped app version)
  - `RELEASE_TAG_PATTERN: '^v[0-9]+\.[0-9]+\.[0-9]+(-nubus[0-9]+)?$'`
- [x] No `KEYCLOAK_VERSION`-style consistency check needed — provisioning has
  no upstream version variable; the tag alone is the version source.
- [ ] Remove `.releaserc`-related leftovers if any; note in CHANGELOG.md that
  entries after v0.70.20 are tag-driven (or freeze the file with a pointer).

## 3. App Center files: `apps/provisioning-service/` → templated `appcenter/`

- [x] Create `appcenter/` (component input `appcenter_file_dir: "appcenter/"`;
  only top-level files are uploaded, `*.jinja` rendered first).
- [x] `ini.jinja`: `Version = {{ APP_VERSION }}` — still review
  `SupportedUcsVersions` (currently `5.2-4 errata346`) vs. component input
  `ucs_base_version`.
- [x] `compose.jinja` — the critical file. For each of the 4 images
  (provisioning-api, -dispatcher, -udm-transformer, -prefill), replace the
  hardcoded `gitregistry.knut.univention.de/...:0.70.10` with the keycloak
  pattern:
  ```jinja
  image: {{ EXTERNAL_PUBLIC_IMAGE_REGISTRY if PUBLIC_RELEASE else EXTERNAL_PRIVATE_IMAGE_REGISTRY }}/provisioning-api:{{ RELEASE_VERSION }}{{ ('@' ~ PROVISIONING_API_DIGEST) if PROVISIONING_API_DIGEST else '' }}
  ```
  (one digest variable per image; digest+tag kept together, keycloak `75e79c1`)
- [x] Keep the `@!@ ... @!@` UCR blocks untouched — verified by local render
  test (all 40 markers preserved).
- [x] NATS image reference stays as the pinned `artifacts.../library/nats`.
- [x] Port `preinst` / `uinst` / `configure_host` / `settings` (plain copies —
  no conffile embedding needed) and `inst.tmpl` → `inst.jinja`: the old
  `%PROVISIONING-BACKUP2MASTER-POST%` sed marker is now
  `{{ "apps/50provisioning-service-backup2master" | source }}`.
  Note: no `logo.svg` in the repo (ini references it; it lives only in the
  Provider Portal — verify the upload keeps it).
- [ ] Retire `apps/push_config_to_appcenter` (superseded by
  `update_appcenter`); keep `apps/50provisioning-service-backup2master`
  (runtime artifact, not release tooling). Coordinate before deleting.

## 4. `.gitlab-ci.yml` changes

- [x] Replace `defaults/nubus-workflow.yaml` with keycloak's custom
  `workflow:` block: parent/pipeline/trigger/schedule sources, MR events,
  protected release tags
  (`$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+(-nubus[0-9]+)?$/ && $CI_COMMIT_REF_PROTECTED == "true"`),
  main, web. One pipeline per MR (no branch pipelines for feature branches,
  keycloak `d802ad9`).
- [x] Include the app-release component (with 4 `container-build` matrix
  needs-entries for the digest artifacts):
  ```yaml
  - component: "$CI_SERVER_FQDN/univention/dev/tooling/ci-components/app-release@2.5.2"
    inputs:
      app_id: "provisioning-service"
      ucs_base_version: "5.2"            # verify against Provider Portal scope
      changelog_link: "<changelog page URL>"
      appcenter_file_dir: "appcenter/"
      release_tag_prefix: "v"
      release_tag_constraint: '[0-9]+\.[0-9]+\.[0-9]+(-nubus[0-9]+)?'
      build_stage: "package"
      release_stage: "publish"
      cleanup_stage: ".post"
      mail_recipient: "app-announcement@univention.de"
      mail_sender: "nubus-core@univention.de"
      author_alias: "Nubus Core Team"
      additional_update_appcenter_needs:
        - "pre-semantic-release"          # RELEASE_VERSION + PUBLIC_RELEASE
        - job: "container-build"          # one needs-entry per image whose
          parallel:                        # digest the compose pins (4×)
            matrix:
              - IMAGE_NAME: "provisioning-api"
                DOCKERFILE_PATH: "docker/events-and-consumer-api/Dockerfile"
          optional: true
        # ... same for provisioning-dispatcher, -udm-transformer, -prefill
  ```
  (matrix needs-entries must match the build matrix exactly; `optional: true`
  because on MRs the image may not have been rebuilt — keycloak pattern)
- [ ] Container job rules (keycloak `fa52360` + `11728e5`): `container-build`,
  `container-malware-scan`, `push-image-external`, `container-sign-external`,
  `container-release-attestation` run
  - always on release tags and main (charts + compose need all digests),
  - on MRs only when the respective sources changed (optional refinement —
    can start with "always on MR" like today and tighten later).
- [x] `create_app_version` overrides (keycloak lines ~276–294 + `e46b24f`):
  - release tag → automatic, env `release-app/${APP_ID}_$CI_COMMIT_TAG`
  - MR → `when: manual`, `allow_failure: true`, env `branch-app/...`,
    `environment: auto_stop_in: "3 days"`
  - main → automatic `999.0.0-staging`, env `staging-app/...`
- [x] `update_appcenter` override — `before_script` exporting one digest per
  image from the build artifacts (keycloak `279da25`, ×4):
  ```sh
  for img in provisioning-api provisioning-dispatcher provisioning-udm-transformer provisioning-prefill; do
    var="$(echo "$img" | tr 'a-z-' 'A-Z_')_DIGEST"
    [ -f "${CI_PROJECT_DIR}/digests/${img}" ] && export "${var}=$(cat "${CI_PROJECT_DIR}/digests/${img}")"
  done
  ```
  (missing digest → compose falls back to the version tag)
- [ ] Helm chart publishing: runs on tag pipelines with
  `RELEASE_VERSION=X.Y.Z` public (chart version jumps 0.45.0 → 2.2.0 — verify
  nothing chokes); main keeps publishing dev chart versions to nubus-dev.
  Charts publish independently of the App Center outcome (keycloak `b0b9b3e`).
- [ ] Tests (`test-unit-and-integration`, `test-end-to-end`, `test-chart-*`)
  on tag pipelines: decide run-or-skip. Keycloak runs its tests; E2E needs the
  testrunner/e2e images which are built on tags anyway. Default: leave rules
  as-is unless they break on tag refs.
- [x] `send_chat_message`: `rules: [when: never]` (keycloak `25ae4b1`).
- [ ] Verify `delete_app_version` env-stop wiring for MR versions works with
  the manual-create override.

## 5. Documentation

- [x] Rewrite `docs/ucs/README.md` (model: keycloak
  `docs/devel/README-testing-release.md`):
  1. MR testing: manually run `create_app_version` → `0.0.0-<slug>` in test
     App Center, installable on test UCS, auto-expires after 3 days;
  2. main keeps `999.0.0-staging` fresh;
  3. release: `git tag -a v2.2.0 -m "..." && git push origin v2.2.0` →
     tag pipeline → verify in Provider Portal → manual `do_release` →
     `check_release` → mail + GitLab release;
  4. re-release via `vX.Y.Z-nubusN`.
- [ ] Document the release-model change (semantic-release → manual tags),
  the 2.1 → 2.2.0 alignment, changelog handling, and retirement of
  `push_config_to_appcenter` / Jenkins `docker-update`.
- [ ] Team announcement: merges no longer auto-release; downstream chart
  consumers get new versions on tags only.

## 6. Validation / rollout

- [ ] MR with everything above: manually run `create_app_version` → verify
  `0.0.0-<slug>` in test App Center, compose renders with nubus-dev images
  and digests; install on a test UCS.
- [ ] Verify MR version cleanup (3-day auto-stop / MR close).
- [ ] Merge → verify main pipeline: dev images/charts to nubus-dev,
  `999.0.0-staging` updated.
- [ ] Tag `v2.2.0` → full tag pipeline: images/charts published publicly,
  App Center version 2.2.0 in test App Center with digest-pinned
  `artifacts.../nubus/images/...` compose.
- [ ] `do_release` + `check_release` → verify production App Center, GitLab
  release, announcement mail.
- [ ] Retire old process artifacts (`push_config_to_appcenter`, Jenkins
  `docker-update` usage) after the first successful release.

## Later / future

- [ ] **semantic-release creates the tags** (original plan, step 2): reintroduce
  semantic-release so merges auto-tag, and have the release pipeline consume
  those tags (note: its `[skip ci]` changelog commit suppresses push-triggered
  tag pipelines → needs an API-trigger job after `post-semantic-release` or a
  manually started pipeline on the tag; digests can be handed over as trigger
  variables). Designed earlier — see git history of this file.
- [ ] **Backend app**: second `app-release` include with `job_prefix` for
  `provisioning-service-backend` + automate the
  `univention-provisioning-service` Debian package via ci-components
  `debian-aptly` / `debian-errata-build` (keycloak uses both).
- [ ] **Dry-run vs. test App Center upload** — clarification:
  - The *test App Center* (`appcenter-test.software-univention.de`) is the
    sandbox: MR (`0.0.0-*`), staging (`999.0.0-staging`) and freshly tagged
    versions live there first and are installable on test UCS systems.
    `create_app_version` + `update_appcenter` only ever touch the test instance.
  - The *only* production-facing step is `do_release` (omar:
    `copy_from_appcenter.test.sh` + `update_mirror.sh`); ci-components offers
    no dry-run mode for it.
  - Closest full dry-run: run the entire tag pipeline and don't confirm the
    manual `do_release` gate — everything real (version creation, templating,
    digest pinning, upload) except the production copy. A `-nubusN` tag can
    rehearse without burning a version number.
  - Possible future ask to ci-components: a `do_release` dry-run that lists
    what *would* be copied, or a scratch app id for rehearsals.
