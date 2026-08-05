# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Command-line interface for Provisioning subscription lifecycle management."""

from __future__ import annotations

import argparse
import os
import socket
import stat
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from .api import APIError, ProvisioningAPI
from .credentials import (
    DEFAULT_ADMIN_CREDENTIAL_FILE,
    AdminCredentialError,
    _validate_server,
    read_local_admin_password,
    read_remote_admin_password,
)
from .manager import LifecycleError, SubscriptionManager
from .models import DefinitionError, SubscriptionDefinition
from .storage import StorageError, SubscriptionStore

DEFAULT_CA_FILE = "/usr/local/share/ca-certificates/ucsCA.crt"
DEFAULT_API_PATH = "/univention/provisioning"


def _add_appcenter_arguments(parser: argparse.ArgumentParser) -> None:
    """Accept the documented arguments forwarded to App Center scripts."""

    parser.add_argument("--binddn", help=argparse.SUPPRESS)
    parser.add_argument("--bindpwdfile", help=argparse.SUPPRESS)
    parser.add_argument("--error-file", help=argparse.SUPPRESS)
    parser.add_argument("--locale", help=argparse.SUPPRESS)
    parser.add_argument("--old-version", help=argparse.SUPPRESS)
    parser.add_argument("--version", help=argparse.SUPPRESS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="univention-provisioning-service-client",
        description="Create and remove managed Nubus Provisioning subscriptions.",
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subscribe = subparsers.add_parser("subscribe", allow_abbrev=False, help="Create or validate a subscription")
    subscribe.add_argument("--json", required=True, help="Complete subscription definition as JSON")
    subscribe.add_argument("--subscription-file", required=True, help="Protected file for subscriber credentials")
    subscribe.add_argument(
        "--provisioning-server",
        default=socket.getfqdn(),
        help="FQDN of the UCS server hosting the Provisioning Service",
    )
    subscribe.add_argument("--generate-password", action="store_true", help="Generate a limited subscriber password")
    subscribe.add_argument(
        "--request-prefill", action="store_true", help="Override the JSON definition to request a prefill"
    )
    subscribe.add_argument(
        "--force",
        action="store_true",
        help="Replace an exact name collision (deletes that subscription's pending queue)",
    )
    subscribe.add_argument(
        "--admin-credential-file",
        default=DEFAULT_ADMIN_CREDENTIAL_FILE,
        help="Local Provisioning Service admin credential file",
    )
    subscribe.add_argument("--ca-file", default=DEFAULT_CA_FILE, help="CA bundle used to verify the Provisioning API")
    _add_appcenter_arguments(subscribe)

    unsubscribe = subparsers.add_parser("unsubscribe", allow_abbrev=False, help="Remove a managed subscription")
    unsubscribe.add_argument("--subscription-file", required=True, help="Protected subscriber credential file")
    unsubscribe.add_argument(
        "--provisioning-server",
        default=socket.getfqdn(),
        help="FQDN of the UCS server hosting the Provisioning Service",
    )
    unsubscribe.add_argument(
        "--admin-credential-file",
        default=DEFAULT_ADMIN_CREDENTIAL_FILE,
        help="Local Provisioning Service admin credential file",
    )
    unsubscribe.add_argument("--ca-file", default=DEFAULT_CA_FILE, help="CA bundle used to verify the Provisioning API")
    _add_appcenter_arguments(unsubscribe)

    hidden = subparsers.add_parser("_read-admin-password", allow_abbrev=False, help=argparse.SUPPRESS)
    hidden.set_defaults(hidden=True)
    return parser


def _is_local_server(server: str) -> bool:
    local_names = {socket.getfqdn().rstrip(".").lower(), socket.gethostname().rstrip(".").lower()}
    return server.rstrip(".").lower() in local_names


def _admin_password_provider(args: argparse.Namespace) -> Callable[[], str]:
    if _is_local_server(args.provisioning_server):
        return lambda: read_local_admin_password(args.admin_credential_file)

    if bool(args.binddn) != bool(args.bindpwdfile):
        raise AdminCredentialError("Both --binddn and --bindpwdfile are required for remote Provisioning access.")
    if args.binddn and args.bindpwdfile:
        return lambda: read_remote_admin_password(args.provisioning_server, args.binddn, args.bindpwdfile)

    # Join scripts on the Primary commonly do not receive bind credentials. In
    # that case the existing local root-protected credential is authoritative,
    # even if a different domain endpoint was explicitly supplied.
    return lambda: read_local_admin_password(args.admin_credential_file)


def _api_for(server: str, ca_file: str) -> ProvisioningAPI:
    validated_server = _validate_server(server)
    return ProvisioningAPI(
        f"https://{validated_server}{DEFAULT_API_PATH}",
        verify=ca_file,
    )


def _write_appcenter_error(path: str | None, message: str) -> None:
    if not path:
        return
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CLOEXEC | os.O_NOFOLLOW)
    except OSError:
        return
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.geteuid():
            return
        os.write(descriptor, (message.rstrip("\n") + "\n").encode("utf-8", "replace"))
    finally:
        os.close(descriptor)


def _print_outcome(action: str, name: str, queue_replaced: bool) -> None:
    if action == "already-absent":
        print("No managed Provisioning subscription was present.")
        return
    print(f"Provisioning subscription {name!r}: {action}.")
    if queue_replaced:
        print(
            "WARNING: The previous subscription and its pending event queue were deleted. "
            "A prefill restores current objects, not discarded historic events.",
            file=sys.stderr,
        )


def _run(args: argparse.Namespace) -> int:
    if args.command == "_read-admin-password":
        # This is the fixed remote half used by univention-ssh. The powerful
        # secret is emitted only to the SSH stdout pipe and is not persisted.
        password = read_local_admin_password()
        sys.stdout.write(password + "\n")
        return 0

    api = _api_for(args.provisioning_server, args.ca_file)
    store = SubscriptionStore(Path(args.subscription_file))
    if args.command == "subscribe":
        definition = SubscriptionDefinition.from_json(args.json)
        if args.request_prefill:
            definition = definition.with_request_prefill(True)
        manager = SubscriptionManager(api, store, _admin_password_provider(args))
        outcome = manager.subscribe(
            definition,
            generate_password=args.generate_password,
            force=args.force,
        )
    else:
        # Normal removal uses only the limited password. The provider remains
        # lazy and is used solely to confirm an absent subscription if a DELETE
        # response may have been lost and the retry is rejected with HTTP 401.
        manager = SubscriptionManager(api, store, _admin_password_provider(args))
        outcome = manager.unsubscribe()
    _print_outcome(outcome.action, outcome.name, outcome.queue_replaced)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (APIError, AdminCredentialError, DefinitionError, LifecycleError, StorageError, ValueError) as exc:
        message = f"Provisioning subscription setup failed: {exc}"
        print(message, file=sys.stderr)
        _write_appcenter_error(getattr(args, "error_file", None), message)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
