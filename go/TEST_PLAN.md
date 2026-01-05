# Integration and Load Test Plan

This document outlines additional integration/e2e tests to add around the Provisioning API Go client and a step‑by‑step plan to implement parallel load tests. These tests assume the provisioning‑api is running via docker‑compose and configuration is provided via environment variables.

## Additional Integration/E2E Tests

- Create with prefill and wait
  - Create a subscription with `request_prefill=true` and poll `GET /v1/subscriptions/{name}` until `prefill_queue_status=done`.
  - Assert status transitions are not `failed` and complete within a timeout.

- Publish + receive simple events
  - Publish N messages via `POST /v1/messages` using a fixed realm/topic (e.g. `udm/tests/topic`).
  - Pull and acknowledge N messages from the subscription; verify bodies match for a subset or all.

- Multiple subscriptions fan‑out
  - Create M subscriptions for the same realms/topics.
  - Publish K messages once and ensure each subscription receives K messages (fan‑out property).

- Parallel pulls per subscription
  - For a single subscription, run C goroutines concurrently calling `messages/next` with small timeouts.
  - Ensure exactly‑once delivery per subscription (no duplicates), then ack. Record latency.

- Cross‑subscription parallel pulls
  - Create M subscriptions; run one worker per subscription pulling and acking messages concurrently.
  - Measure per‑subscription and aggregate latency.

- Timeout behavior (empty queue)
  - Call `messages/next` with a small timeout on an empty queue and assert a `null` response within the timeout budget.

- Acknowledgement behavior
  - Pull a message and delay acknowledgement to observe redelivery count (`num_delivered`) on a subsequent get.
  - Then acknowledge with status `ok` and verify it is not redelivered again.

- Authentication/authorization
  - Wrong password retrieving a subscription should return 401.
  - Deleting a subscription with subscriber credentials should be allowed or rejected in accordance with API policy; verify behavior.

- Message ordering (per subscription)
  - Publish a known sequence of messages; assert `sequence_number` monotonicity and body order when pulling sequentially.

- Pop flag semantics (when available)
  - Exercise `pop=true` vs default behavior and verify visibility and acknowledgement implications once the server supports it reliably.

- UDM‑origin messages (optional later)
  - Create objects via UDM REST API to trigger messages and validate mapping to queue messages (e.g., ensure `new.dn` matches created DN).

## Load Test Plan (Parallel, Multi‑Subscription)

### Goals

- Measure end‑to‑end latency for:
  - `GET /v1/subscriptions/{name}/messages/next`
  - `PATCH /v1/subscriptions/{name}/messages/{seq}/status`
- Exercise parallel consumption across many subscriptions and optionally multiple workers per subscription.
- Report min/avg/p95/p99/max, throughput, error/timeout counts; configurable thresholds (e.g., avg < 50ms, max < 150ms).

### Approach

- Form factor
  - Provide a standalone Go binary (e.g., `go/cmd/perftests`) for longer runs and richer reporting.
  - Optionally provide `go test` entry points guarded by a build tag (e.g., `// +build perf`) for quick CI gating.

- Configuration (env + flags)
  - Env: `PROVISIONING_API_BASE_URL`, `PROVISIONING_ADMIN_USERNAME`, `PROVISIONING_ADMIN_PASSWORD`, `PROVISIONING_EVENTS_USERNAME`, `PROVISIONING_EVENTS_PASSWORD`.
  - Flags: `--subs` (M), `--msgs` (K), `--workers-per-sub` (C), `--timeout`, `--duration`, `--prefill`, `--realm`, `--topic`, `--threshold-avg-ms`, `--threshold-max-ms`, `--json-out`.

- Setup
  - Create M subscriptions with unique names/passwords for isolation; record credentials per subscription.
  - If `--prefill`, poll until `prefill_queue_status=done` or timeout; record prefill timing.

- Data generation
  - For load, publish K messages via Events API (simple body) once per run; all subscriptions should receive them (fan‑out).
  - Optionally support steady‑state mode (`--duration`) with a background publisher pacing messages.

- Workers and concurrency
  - Use one goroutine per subscription by default; optionally C workers per subscription pulling concurrently.
  - Use a shared `http.Client` with tuned `Transport` (keep‑alive, MaxIdleConnsPerHost).
  - Manage lifecycle with `errgroup.Group` and a root `context.Context` for cancellation.

- Measurements and metrics
  - Capture timestamps around `messages/next` and `ack` for every message processed.
  - Aggregate per‑subscription and global metrics: count, min, avg, p95/p99, max; error/timeout counts.
  - Compute throughput: messages/sec (overall and per subscription).
  - Output human‑readable summary and optional JSON for downstream analysis (e.g., benchstat or dashboards).

- Validation
  - For simple messages, sample or fully verify that returned body matches what was published.
  - Confirm that each subscription processed exactly K messages (or expected count in duration mode).

- Cleanup
  - Delete all created subscriptions at the end (best‑effort), with per‑subscription timeout.
  - Use unique names to avoid reliance on stream purge, keeping tests isolated.

### Phased Implementation

1. Minimal load tool
   - Inputs: `--subs`, `--msgs`, `--timeout`, `--prefill`.
   - Steps: create M subs -> publish K messages -> parallel pull+ack -> print min/avg/max and counts -> cleanup.

2. Enhanced metrics
   - Add p95/p99, histogram, throughput; export JSON.
   - Add configurable thresholds to return non‑zero exit codes on regressions.

3. Concurrency controls
   - Add `--workers-per-sub`, back‑pressure handling, per‑request context timeouts.

4. Duration mode
   - Support `--duration`; background publisher pacing at a set QPS; dynamic worker loops until context deadline.

5. Scenarios and toggles
   - Optional prefill per subscription; mixed realms/topics; larger payloads to simulate realistic sizes.
   - Toggle correctness checks vs sampling for higher throughput runs.

### Potential Pitfalls and Mitigations

- Server `pop` semantics may not be stable; keep it disabled by default.
- Empty queue long‑polling should return `null`; treat as no‑message and continue.
- Redelivery may occur if acknowledgements are delayed or dropped; track `num_delivered` for insight.
- Ensure generous but bounded timeouts to prevent test hangs; always honor root context cancellation.

### Artifacts and Locations

- Binary: `go/cmd/perftests` (main package)
- Library reuse: `go/client` for HTTP calls and types
- Documentation: `go/perftests/README.md` with usage examples and expected outputs

