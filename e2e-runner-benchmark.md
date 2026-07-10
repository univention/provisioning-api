<!--
SPDX-License-Identifier: AGPL-3.0-only
SPDX-FileCopyrightText: 2026 Univention GmbH
-->

# e2e runner benchmark

Comparing the `test-end-to-end` wall-clock across GitLab runner types, to evaluate
moving the e2e job from the K8s/dind runners onto the faster Plusserver `dae-*`
runners (Docker-outside-of-Docker, see `.gitlab-ci.yml`).

Durations are the GitLab **job** duration (includes image pulls, `compose up`,
the pytest run, and teardown), not just the test execution.

## Baseline — current production path (`main`, K8s runner "brained")

The e2e job on `main` runs via the `.dind` template (tag `docker`) on the
`K8s Gitlab Runner (brained)`. Successful runs only (failed pipelines skipped):

| Pipeline | Date       | Duration |
| -------- | ---------- | -------- |
| 425638   | 2026-07-10 | 303 s    |
| 425496   | 2026-07-09 | 305 s    |
| 424958   | 2026-07-08 | 303 s    |
| 424404   | 2026-07-07 | 454 s    |
| 422787   | 2026-07-02 | 431 s    |

**Median ≈ 305 s** (three most recent tightly clustered at ~303–305 s, with
occasional ~430–450 s outliers).

## dae-* runners (DooD) — `jlohmer/dind`

Each `dae` flavor runs the identical `.e2e-test` job (only `tags` differ), 3 runs
each for repeatability.

<!-- RESULTS -->
_Pending — populated from pipeline runs on `jlohmer/dind`._
<!-- /RESULTS -->
