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
Job **duration** in seconds; ✓/✗ = job pass/fail. The e2e suite is flaky (a
different flavor fails most runs, independent of size — `pull`/`up` always
succeed), so treat pass/fail as noise and **durations** as the signal.

| Pipeline | Cache state | dae-s | dae-m | dae-l | dae-xl |
| -------- | ----------- | ----- | ----- | ----- | ------ |
| #425831  | s warm, m/l/xl **cold** | 160 ✓ | 292 ✗ | 305 ✗ | 276 ✓ |
| #425833  | warm                    | 195 ✗ | 152 ✓ | 237 ✗ | 175 ✗ |
| #425835  | warm                    | 164 ✓ | 185 ✗ | 156 ✗ | 177 ✗ |
| #425836  | **cold** (ran concurrently with #425835, so the autoscaler spun fresh instances) | 320 ✗ | 278 ✗ | 196 ✗ | 250 ✗ |

### Findings

- **Warm ≈ 155–195 s across every flavor** (#425833, #425835) — roughly **half**
  the ~305 s K8s baseline. This is the real DooD win.
- **VM size barely matters.** Warm, `dae-s` (164 s) is as fast as `dae-xl`
  (177 s); the workload is dominated by fixed waits (`sleep 10`, service
  readiness, pytest network waits), not CPU. Bigger flavors don't help.
- **Cache warmth is the dominant variable.** A cold instance adds ~100–160 s:
  job-image pull ~60 s + `compose pull` of the provisioning/nats/ldap images
  ~30–70 s. First run per instance (#425831 m/l/xl, all of #425836) shows this.
- **Concurrency forces cold instances.** #425836 ran alongside #425835, so the
  autoscaler booted fresh cold VMs and lost the warm advantage entirely.

### Takeaway

Prefer **`dae-s`** — size buys nothing for this job. The ~2× speedup vs the K8s
baseline comes from DooD **plus** warm caches, so the levers that matter are
keeping instances warm (idle-count / reuse) and pre-baking the common images,
**not** a larger flavor. The test suite's flakiness is a separate issue.
<!-- /RESULTS -->
