# Performance Test Architecture

This document outlines how to build performance tests by reusing pieces from the existing integration/e2e tests and adding a thin timing/orchestration layer.

## Reusable From Integration Tests

- Client initialization
  - `adminClient` from env and `eventsClient = adminClient.Fork(...)` to share a single Transport.
  - `Fork(username, password)` to create many subscription-scoped clients without losing connection reuse.
- Subscription lifecycle
  - `createTestSubscription(ctx, realmsTopics, requestPrefill) (*Client, cleanup)` returns an isolated subscription client and a deferrable teardown.
  - `DeleteSubscription` cleanup keeps test runs independent.
- Message model
  - `dummyMessage(count int)` returns a small, predictable payload for assertions and repeatable load.
- Server long-polling
  - `GetNextMessage(ctx, name, timeout, pop)` accepts a `time.Duration` for long-poll; use this instead of sleeps.

## Useful With Light Tweaks

- Message polling helper
  - Adapt `getMessages` into a worker that pulls and acknowledges messages in a loop and captures timings.
  - No sleeps; only use server long-poll (e.g., 100 ms) to pace.
- Warm-up phase
  - Keep a short mapping warm-up (e.g., one second or a couple of non-measured gets) to avoid cold-start effects. Do not include this time in measurements.

## Perf-Specific Helpers To Add

- Publisher utility
  - `publishN(ctx, eventsClient, N)` — send `dummyMessage(i)` for `i=0..N-1`.
- Worker
  - `worker(ctx, subClient, subName, N, timeout) (getLatencies, ackLatencies, counts, error)`
    - Loop N times: measure `GetNextMessage` duration, then measure `AckMessage` duration.
    - Use immediate ack to avoid redelivery noise.
- Metrics and stats
  - Collect per-call latencies and compute: count, min, avg, p95/p99, max; error/timeouts.
  - Aggregate per-subscription and global statistics for reporting and assertions.

## Orchestration Flow

1. Setup
   - Create M subscriptions with `createTestSubscription` (optionally `requestPrefill=false/true`).
   - Warm-up dispatcher mapping (brief sleep or one non-measured `GetNextMessage`).
2. Publish
   - Publish K messages once via `eventsClient` (fan-out delivers K to each subscription).
3. Parallel pull
   - Start M goroutines (one per subscription) using `errgroup.Group`.
   - Each worker pulls K messages with server long-poll (e.g., `100*time.Millisecond`) and acks immediately.
4. Aggregate and assert
   - Compute per-subscription and global stats.
   - Assert thresholds (e.g., `avg < 50ms`, `max < 150ms`), configurable via env.

## Configuration

- Environment variables (reusing integration env):
  - `PROVISIONING_API_BASE_URL`, `PROVISIONING_ADMIN_USERNAME`, `PROVISIONING_ADMIN_PASSWORD`, `PROVISIONING_EVENTS_USERNAME`, `PROVISIONING_EVENTS_PASSWORD`.
- Performance parameters via env for simplicity:
  - `PERF_SUBS` (M), `PERF_MSGS` (K), `PERF_TIMEOUT_MS` (long-poll), `PERF_PREFILL` (bool).
  - Thresholds: `PERF_MAX_AVG_MS`, `PERF_MAX_P95_MS`, `PERF_MAX_MAX_MS`.

## What To Avoid

- Sleeping between polls — rely on server long-poll only.
- Printing per-message timings — collect and summarize; keep output concise.
- Mixing credentials at call sites — keep auth bound to client instances.
- Over-validating payloads — a quick check on the `count` marker is sufficient for perf.

## Notes

- `GetNextMessage` negative timeout omits the param and uses the server default; a small positive timeout (e.g., 100 ms) gives responsive sampling without busy-waiting.
- Keep subscription names unique per run and always delete them to avoid residual load and cross-test interference.
- For broader runs, consider JSON output for metrics so results can be compared or graphed.

