# NATS Disruption Tests

These tests verify the resilience of the provisioning system during NATS failures and service interruptions.

## Preparation

1. **Deactivate auto-restart** in docker-compose.yaml:
   ```yaml
   # Remove restart: always/unless-stopped from all services
   ```

2. **Start the provisioning system**:
   ```bash
   docker compose up --remove-orphans provisioning-api dispatcher udm-transformer nats1 nats2 nats3 prefill udm-listener ldap-notifier udm-rest-api ldap-server

   # After testing cleanup:
   docker compose down --remove-orphans --volumes
   ```

## Scripts

### 1. Service Monitoring (`scripts/provisioning-mon.sh`)

Monitors services and automatically restarts them on crashes.

**Usage**:
```bash
# Default: monitors udm-listener
./scripts/provisioning-mon.sh

# Monitor specific service:
./scripts/provisioning-mon.sh dispatcher
./scripts/provisioning-mon.sh prefill
./scripts/provisioning-mon.sh udm-transformer
./scripts/provisioning-mon.sh udm-listener
```

**Functionality**:
- Continuously monitors if the service is running
- On crash: saves last 200 log lines to `<service>.crash.<timestamp>.log`
- Automatically restarts the service
- Logs all activities to `<service>.mon.log`

### 2. NATS Monitoring (`scripts/provisioning-nats-mon.sh`)

Shows live status of NATS streams and key-value stores.

**Usage**:
```bash
./scripts/provisioning-nats-mon.sh
```

**Functionality**:
- Shows all NATS streams every 0.5 seconds
- Shows all entries in the SUBSCRIPTIONS KV store
- Live updates of NATS cluster information

### 3. Test Loop (`scripts/provisioning-loop-test.sh`)

Continuously runs provisioning tests.

**Usage**:
```bash
cd <root>/e2e_tests

# With automatic cleanup between tests (current summaries were created this way):
../nats_disruption_tests/scripts/provisioning-loop-test.sh

# Without cleanup (for performance tests):
../nats_disruption_tests/scripts/provisioning-loop-test.sh no-cleanup
```

**Functionality**:
- Runs the following tests in an infinite loop:
  - `tests/test_workflow.py::test_prefill_with_multiple_topics`
  - `tests/test_consumer_client.py::test_get_multiple_messages`
- Automatically cleans up between tests:
  - Deletes all SUBSCRIPTIONS KV entries
  - Deletes all numbered streams
- Logs all output to `../provisioning-loop-test.log`

### 4. NATS Restart Loop (`scripts/provisioning-nats-restart-loop.sh`)

Simulates NATS cluster failures through regular restarts.

**Usage**:
```bash
./scripts/provisioning-nats-restart-loop.sh
```

**Functionality**:
- Restarts all NATS servers (`nats1`, `nats2`, `nats3`) every 40 seconds
- Simulates network interruptions and cluster failures

## Complete Test Procedure

Open multiple terminals and run the following commands in parallel:

### Terminal 1: Start NATS monitoring
```bash
cd nats_disruption_tests
./scripts/provisioning-nats-mon.sh
```

### Terminal 2-5: Start service monitoring
```bash
# Terminal 2
./scripts/provisioning-mon.sh dispatcher

# Terminal 3
./scripts/provisioning-mon.sh prefill

# Terminal 4
./scripts/provisioning-mon.sh udm-transformer

# Terminal 5
./scripts/provisioning-mon.sh udm-listener
```

### Terminal 6: Start test loop
```bash
./scripts/provisioning-loop-test.sh
```

### Terminal 7: Start NATS restart loop
```bash
./scripts/provisioning-nats-restart-loop.sh
```

## Expected Behavior

- **Services**: Crash occasionally and are automatically restarted
- **Tests**: Run continuously, even during service failures
- **NATS**: Is restarted regularly, tests should still succeed
- **Logs**: Crash logs and monitor logs document all events

## Log Files

- `provisioning-loop-test.log`: Output of all tests
- `<service>.mon.log`: Monitor activities per service
- `<service>.crash.<timestamp>.log`: Crash details with last 200 log lines

## Stopping the Tests

All scripts run indefinitely. Stop with `Ctrl+C` in each terminal or:
```bash
docker compose down --remove-orphans --volumes
```

## Analysis

For each `<service>` of
* dispatcher
* prefill
* udm-transformer
* udm-listener

create a summary by calling

```
ls -1 <service>.crash.*log \
    | xargs -i bash -c "echo {}; ./scripts/parse-crash-logs.sh {} \
    | grep -E 'ROOT|ERROR'" | tee <service>.errors.log

grep -Eo "Primary issue.*" <service>.errors.log  \
    | sort -u | tee -a <service>.errors.summary.log

grep -Eo "ERROR.*ROOT" prefill.errors.log  \
    | sed -re 's|http://.*ROOT||;s| ROOT||' \
    | sort -u | tee -a <service>.errors.summary.log
```
