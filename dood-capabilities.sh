#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

#
# dood-capabilities.sh
# Probe whether this VM can run the CI e2e job in "Docker-outside-of-Docker"
# (DooD) mode: a job container that talks to the *host* dockerd via the mounted
# /var/run/docker.sock, instead of spinning up a docker:dind service sidecar.
#
# Companion to vm-capabilities.sh (CPU/mem/disk). This one answers the specific
# question: "can we drop `extends: .dind` and just socket-mount the host daemon
# on the dae-* runners?" It exercises the exact things the e2e job needs:
#   - reach the host daemon from inside a container (socket mount)
#   - start containers from that container
#   - relative bind-mounts resolve correctly (the big DooD gotcha)
#   - --privileged and --network host are permitted
#   - `docker compose` works over the host socket end-to-end
#   - none of the e2e stack's host ports are already taken
#
# Read-only w.r.t. the host except for a throwaway temp dir under $PWD and a few
# short-lived probe containers, all cleaned up on exit.
#
# Usage:
#   ./dood-capabilities.sh                     # full run
#   PROBE_IMAGE=docker:cli ./dood-capabilities.sh   # override job-image proxy
#   NO_PULL=1 ./dood-capabilities.sh           # fail instead of pulling images
#
# Output is plain text meant to be copy-pasted back verbatim.

set -uo pipefail

# A DOCKER_API_VERSION pin (e.g. an inherited CI var =1.39) force-downgrades the
# client and a modern host daemon (>=29.x, min API 1.40) rejects every call.
# Clear it so the client negotiates the API version with the server.
unset DOCKER_API_VERSION

# Use the same docker CLI image the pipeline job uses as the DooD stand-in, so we
# test the *same* client/compose. Matches the VM host daemon (29.6.1).
PROBE_IMAGE="${PROBE_IMAGE:-docker:29.6.1}"
ALPINE="${ALPINE:-alpine:3.20}"
SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"

hr()   { printf -- '---- %s %s\n' "$1" "$(printf -- '-%.0s' $(seq 1 $((60 - ${#1}))))"; }
have() { command -v "$1" >/dev/null 2>&1; }
ok()   { printf '  [ OK ] %s\n' "$1"; }
no()   { printf '  [FAIL] %s\n' "$1"; }
info() { printf '  [info] %s\n' "$1"; }

# --- scratch + cleanup -------------------------------------------------------
WORK="$PWD/.dood-probe.$$"
CIDS=()
cleanup() {
  for c in "${CIDS[@]:-}"; do docker rm -f "$c" >/dev/null 2>&1; done
  docker rm -f dood_probe_net >/dev/null 2>&1
  rm -rf "$WORK" 2>/dev/null
}
trap cleanup EXIT
mkdir -p "$WORK"

echo "======== DooD CAPABILITIES ========"
echo "date(UTC):   $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "host:        $(hostname 2>/dev/null)"
echo "probe image: $PROBE_IMAGE"
echo "socket:      $SOCK"
echo

# --- 0. docker CLI present ---------------------------------------------------
if ! have docker; then
  no "docker CLI not found on the VM. Everything below is moot; install docker first."
  exit 1
fi

# --- pre-pull the probe images ----------------------------------------------
hr "IMAGE PULL"
for img in "$PROBE_IMAGE" "$ALPINE"; do
  if docker image inspect "$img" >/dev/null 2>&1; then
    info "$img already present"
  elif [ "${NO_PULL:-0}" = "1" ]; then
    no "$img missing and NO_PULL=1; skipping tests that need it"
  else
    if docker pull -q "$img" >/dev/null 2>&1; then ok "pulled $img"; else no "could not pull $img"; fi
  fi
done
echo

# --- 1. socket presence + access --------------------------------------------
hr "1. HOST DOCKER SOCKET"
echo "  user:   $(id -un)  uid=$(id -u)  groups=$(id -Gn 2>/dev/null)"
if [ -S "$SOCK" ]; then
  ok "$SOCK exists"
  ls -l "$SOCK" 2>/dev/null | sed 's/^/         /'
  info "socket group: $(stat -c '%G (gid %g)' "$SOCK" 2>/dev/null)"
else
  no "$SOCK is not a socket. DooD via host daemon is impossible on this VM as-is."
fi
if docker version --format '{{.Server.Version}}' >/dev/null 2>&1; then
  ok "current user can talk to the daemon (server $(docker version --format '{{.Server.Version}}' 2>/dev/null))"
else
  no "current user cannot talk to the daemon directly (need root / docker group). Runner runs as root, so this may still be fine."
fi
echo

# --- 2. reach host daemon from inside a container (the core of DooD) ---------
hr "2. REACH HOST DAEMON FROM A CONTAINER"
out=$(docker run --rm -v "$SOCK:/var/run/docker.sock" "$PROBE_IMAGE" \
        docker version --format 'server={{.Server.Version}} api={{.Server.APIVersion}}' 2>&1)
if printf '%s' "$out" | grep -q '^server='; then
  ok "container reached host daemon: $out"
else
  no "container could NOT reach host daemon via socket mount:"
  printf '%s\n' "$out" | sed 's/^/         /'
fi
echo

# --- 3. start a container from within a container ----------------------------
hr "3. START A CONTAINER FROM INSIDE A CONTAINER"
out=$(docker run --rm -v "$SOCK:/var/run/docker.sock" "$PROBE_IMAGE" \
        docker run --rm "$ALPINE" echo "hello-from-nested" 2>&1)
if printf '%s' "$out" | grep -q 'hello-from-nested'; then
  ok "nested 'docker run' works (container started a sibling container on the host)"
else
  no "could not start a sibling container from inside the job container:"
  printf '%s\n' "$out" | tail -3 | sed 's/^/         /'
fi
echo

# --- 4. RELATIVE BIND-MOUNT SEMANTICS (the DooD gotcha) ----------------------
# When the in-container docker client hits the host daemon, `-v ./x:/y` is
# resolved on the HOST fs, not inside the job container. The e2e compose file is
# full of relative binds (./tests/..., ./nats.dev.conf). They only work if the
# job's working dir is a HOST path mounted into the job container at the SAME
# absolute path. This section proves whether that pattern holds here.
hr "4. RELATIVE BIND-MOUNT PATH CONSISTENCY"
echo "test_marker_$$" > "$WORK/marker"
# 4a. host-path mount (workdir mounted at same path) -> should see the marker.
out=$(docker run --rm -v "$SOCK:/var/run/docker.sock" -v "$WORK:$WORK" -w "$WORK" \
        "$PROBE_IMAGE" docker run --rm -v "$WORK/marker:/m:ro" "$ALPINE" cat /m 2>&1)
if printf '%s' "$out" | grep -q "test_marker_$$"; then
  ok "host-path bind-mount visible to the sibling container (workdir==host path)."
  info "=> CI must mount the builds dir at the same absolute path (privileged+host builds volume)."
else
  no "host-path bind-mount NOT visible; relative binds in the compose file will break:"
  printf '%s\n' "$out" | tail -3 | sed 's/^/         /'
fi
# 4b. container-only file (NOT on host) -> demonstrates the failure mode.
out=$(docker run --rm -v "$SOCK:/var/run/docker.sock" "$PROBE_IMAGE" sh -c \
        'echo secret > /tmp/only-in-job; docker run --rm -v /tmp/only-in-job:/m "'"$ALPINE"'" cat /m 2>&1 | head -1' 2>&1)
if printf '%s' "$out" | grep -q 'secret'; then
  info "unexpected: a job-container-only path was visible (bind daemon shares the job fs?)."
else
  info "as expected: a file that exists ONLY inside the job container is NOT mountable"
  info "  (host daemon resolves the path on the host). Anything you 'docker cp' or write"
  info "  inside the job and then try to bind-mount must live on a shared host path first."
fi
echo

# --- 5. privileged -----------------------------------------------------------
hr "5. --privileged PERMITTED"
out=$(docker run --rm --privileged "$ALPINE" sh -c 'ip link add dummy0 type dummy && echo priv-ok' 2>&1)
if printf '%s' "$out" | grep -q 'priv-ok'; then
  ok "daemon allows --privileged (created a dummy netdev inside a privileged container)"
else
  info "privileged netdev test inconclusive (kernel module?):"
  printf '%s\n' "$out" | tail -2 | sed 's/^/         /'
fi
info "NB: whether *job* containers get --privileged is a runner config.toml setting, not testable from the VM alone."
echo

# --- 6. host networking + e2e port availability ------------------------------
hr "6. HOST NETWORKING + e2e PORT COLLISIONS"
out=$(docker run --rm --network host "$ALPINE" sh -c 'echo host-net-ok' 2>&1)
if printf '%s' "$out" | grep -q 'host-net-ok'; then
  ok "--network host permitted"
else
  no "--network host failed: $(printf '%s' "$out" | tail -1)"
fi
# e2e stack host-published ports (docker-compose.yaml). Under host networking a
# second concurrent job collides on these; and anything already listening breaks
# a single job too. See hackathon decisions.md D7.
E2E_PORTS="389 636 4222 4223 8222 6669 7777 8001 9979 9980"
busy=""
for p in $E2E_PORTS; do
  if have ss; then ss -ltn 2>/dev/null | grep -qE "[:.]$p[[:space:]]" && busy="$busy $p"
  elif have netstat; then netstat -ltn 2>/dev/null | grep -qE "[:.]$p[[:space:]]" && busy="$busy $p"; fi
done
if [ -n "$busy" ]; then
  no "these e2e host ports are ALREADY in use on the VM:$busy"
else
  ok "none of the e2e host ports are currently in use ($E2E_PORTS)"
fi
info "under network_mode=host, two concurrent e2e jobs on one VM WILL collide on these ports (D7)."
echo

# --- 7. docker compose over the host socket, end to end ----------------------
# Mirrors the real job: cd into a host workdir mounted at the same path, then
# `docker compose up` a tiny stack with a relative bind mount and a host port.
hr "7. docker compose OVER HOST SOCKET (mini e2e simulation)"
cver=$(docker run --rm "$PROBE_IMAGE" docker compose version --short 2>&1)
if printf '%s' "$cver" | grep -qE '^v?[0-9]'; then
  ok "compose plugin present in $PROBE_IMAGE (v$cver)"
else
  no "no 'docker compose' in $PROBE_IMAGE — the e2e job image needs the compose plugin:"
  printf '%s\n' "$cver" | tail -2 | sed 's/^/         /'
fi
cat > "$WORK/docker-compose.yml" <<YAML
services:
  probe:
    image: $ALPINE
    command: ["sh","-c","cat /etc/probe-marker && echo compose-dood-ok"]
    volumes:
      - ./marker:/etc/probe-marker:ro
YAML
out=$(docker run --rm -v "$SOCK:/var/run/docker.sock" -v "$WORK:$WORK" -w "$WORK" \
        "$PROBE_IMAGE" sh -c 'docker compose up --abort-on-container-exit --no-log-prefix 2>&1; docker compose down -v >/dev/null 2>&1' 2>&1)
if printf '%s' "$out" | grep -q 'compose-dood-ok'; then
  ok "'docker compose up' over the host socket works, with a relative bind mount"
else
  no "compose-over-host-socket simulation failed:"
  printf '%s\n' "$out" | tail -6 | sed 's/^/         /'
fi
echo

# --- 8. verdict --------------------------------------------------------------
hr "VERDICT"
echo "  If sections 2, 3, 4a and 7 are OK, this VM supports running the e2e job in"
echo "  DooD mode (host socket, no docker:dind sidecar). Remaining requirements are"
echo "  RUNNER-SIDE (config.toml), not VM-side:"
echo "    volumes    = [\"/var/run/docker.sock:/var/run/docker.sock\", \"/cache\"]"
echo "    privileged = true"
echo "    # network_mode = \"host\" only if the job needs host ports (see D7 collision risk)"
echo "======== END ========"
