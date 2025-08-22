#!/bin/bash
#
# ucs-backup2master-and-reinit-provisioning.sh
#
# Promotes a UCS Backup Directory Node to Primary (Master)
# and reinitializes the "provisioning" app afterwards.
#
# Usage: sudo ./ucs-backup2master-and-reinit-provisioning.sh
# Optional env:
#   APP_NAME=provisioning   # override if needed
#   NONINTERACTIVE=1        # auto-confirm interactive fixes in backup2master step
#   SKIP_PROMOTION=1        # only (re)initialize the app, do not promote
#   DRY_RUN=1               # show what would run
#
set -euo pipefail

APP_NAME="${APP_NAME:-provisioning}"
LOG_DIR="/var/log/univention"
SCRIPT_LOG="${LOG_DIR}/backup2master_and_${APP_NAME}.log"
PROMOTE_LOG="${LOG_DIR}/backup2master.log"
DRY_RUN="${DRY_RUN:-0}"

exec > >(tee -a "$SCRIPT_LOG") 2>&1

echo "=== $(date -Is) :: Starting UCS Backup->Master promotion + app reinitialize (${APP_NAME}) ==="

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: Required command '$1' not found in PATH." >&2
    exit 1
  fi
}

run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[DRY-RUN] $*"
  else
    echo "+ $*"
    eval "$@"
  fi
}

# --- Pre-flight checks ---
require_cmd ucr
require_cmd univention-app
require_cmd univention-run-join-scripts

ROLE="$(ucr get server/role || true)"
if [[ -z "$ROLE" ]]; then
  echo "ERROR: Could not determine UCS server role via UCR." >&2
  exit 1
fi
echo "Detected server role: ${ROLE}"

if [[ "${SKIP_PROMOTION:-0}" != "1" ]]; then
  if [[ "$ROLE" != "domaincontroller_backup" ]]; then
    echo "ERROR: This system is not a Backup Directory Node (found: ${ROLE}). Aborting."
    exit 1
  fi

  echo "IMPORTANT: Ensure the old Master is powered OFF and unreachable before continuing."
  echo "This conversion is NOT reversible."
  sleep 2
fi

# --- Optional: sanity info for DNS and repository reachability (best-effort) ---
MASTER_HOST="$(ucr get ldap/master || true)"
if [[ -n "$MASTER_HOST" ]]; then
  echo "Current ldap/master in UCR: ${MASTER_HOST}"
fi

# --- App Center cache refresh (harmless) ---
echo "Refreshing App Center cache..."
run "univention-app update"

# --- Promotion: Backup -> Master ---
if [[ "${SKIP_PROMOTION:-0}" != "1" ]]; then
  echo "Starting promotion using /usr/lib/univention-ldap/univention-backup2master ..."
  # The tool is interactive when it finds leftover refs; NONINTERACTIVE lets you auto-accept.
  if [[ "${NONINTERACTIVE:-0}" == "1" ]]; then
    # Feed 'yes' to suggested fixes step
    run "yes | /usr/lib/univention-ldap/univention-backup2master"
  else
    run "/usr/lib/univention-ldap/univention-backup2master"
  fi

  echo "Promotion finished. Details logged to ${PROMOTE_LOG}."
  echo "Rebooting is required by the official procedure. Rebooting now..."
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[DRY-RUN] Reboot skipped."
  else
    sleep 2
    systemctl reboot
    # The script will stop here due to reboot. If you want to auto-continue after reboot,
    # place the app reinit part in a systemd oneshot or cron @reboot hook.
  fi
fi

# If we’re here, either SKIP_PROMOTION=1 or DRY_RUN=1. Continue with app reinitialize.
echo "Proceeding to reinitialize app: ${APP_NAME}"

# --- Verify app is installed / known ---
if ! univention-app info | grep -q -E "^\s*${APP_NAME}\s"; then
  echo "WARNING: App '${APP_NAME}' not found in 'univention-app info'. Attempting anyway..."
fi

# Reinitialize: this recreates the app container with current settings.
# This is supported by the App Center and is commonly used by several UCS apps
# to apply updated configuration. (See docs and forum references.)
echo "Reinitializing ${APP_NAME}..."
run "univention-app reinitialize ${APP_NAME}"

# Optionally, ensure services are up
echo "Restarting ${APP_NAME} to be safe..."
run "univention-app restart ${APP_NAME}"

# Post-join scripts (often needed after role changes / app operations)
echo "Running univention join scripts (best-effort)..."
run "univention-run-join-scripts || true"

echo "=== $(date -Is) :: Completed. Log: ${SCRIPT_LOG} ==="