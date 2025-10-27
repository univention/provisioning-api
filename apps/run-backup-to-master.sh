#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

#
# ucs-backup2master-and-reinit-provisioning.sh
#
# Promotes a UCS Backup Directory Node to Primary (Master)
# and reinitializes the "provisioning" app afterwards.
#
# Usage: sudo ./ucs-backup2master-and-reinit-provisioning.sh
# Optional env:
#   APP_NAME=provisioning-service   # override if needed
#   DRY_RUN=0               # show what would run
#
set -euo pipefail

APP_NAME="${APP_NAME:-provisioning-service}"
APP_BACKEND_NAME="${APP_BACKEND_NAME:-provisioning-service-backend}"
LOG_DIR="/var/log/univention"
SCRIPT_LOG="${LOG_DIR}/backup2master_and_${APP_NAME}.log"
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

# --- Check installed apps ---

# --- Check APP_NAME is installed and backend not yet installed ---
if ! univention-app info | grep -P '^(?=.*\bprovisioning-service=[^ ]+\b)(?!.*\bprovisioning-service-backend=[^ ]+\b).*' > /dev/null; then
  echo "ERROR: App '${APP_NAME}' not installed or backend '${APP_BACKEND_NAME}' already installed." >&2
  exit 1
fi


# --- Check current server role ---
ROLE="$(ucr get server/role)"
if [[ -z "$ROLE" ]]; then
  echo "ERROR: Could not determine UCS server role via UCR." >&2
  exit 1
fi
echo "Detected server role: ${ROLE}"

if [[ "$ROLE" != "domaincontroller_master" ]]; then
  echo "ERROR: This system is not a Master Directory Node (found: ${ROLE}). Aborting."
  exit 1
fi

# --- App Center cache refresh (harmless) ---
echo "Refreshing App Center cache..."
run "univention-app update"

# --- Install backend app ---
run "univention-app install --noninteractive '${APP_BACKEND_NAME}' || {
  echo 'ERROR: Failed to install backend app "${APP_BACKEND_NAME}".' >&2
  exit 1
}"

# Reinitialize: this recreates the app container with current settings.
# This is supported by the App Center and is commonly used by several UCS apps
# to apply updated configuration. (See docs and forum references.)
echo "Reinitializing ${APP_NAME}..."
run "univention-app reinitialize ${APP_NAME}"

echo "=== $(date -Is) :: Completed. Log: ${SCRIPT_LOG} ==="
