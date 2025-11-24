#!/usr/bin/python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import os
import signal
import time
import traceback

import psutil

from univention.listener.handler import ListenerModuleHandler
from univention.provisioning.listener.config import ldap_producer_settings
from univention.provisioning.listener.mq_adapter_nats import MessageQueueNatsAdapter
from univention.provisioning.listener.mq_port import MessageQueuePort

name = "nubus-provisioning"


class LdapListener(ListenerModuleHandler):
    class Configuration(ListenerModuleHandler.Configuration):
        name = name
        description = "Listener module that forwards LDAP changes to the UDM Transformer."
        ldap_filter = "(objectClass=*)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = ldap_producer_settings()
        try:
            self.mq: MessageQueuePort = MessageQueueNatsAdapter(self.settings)
            self._ensure_queue_exists()
        except Exception as error:
            self.logger.error("Failed to initialize the NATS queue: %r", error)
            traceback.print_exc()
            self.kill_listener_process()
            raise

    def create(self, dn, new):
        self.logger.info("[ create ] dn: %r", dn)
        self._send_message(new, {})

    def modify(self, dn, old, new, old_dn):
        if old_dn:
            self.logger.info("[ modify & move ] dn: %r old_dn: %r", dn, old_dn)
        else:
            self.logger.info("[ modify ] dn: %r", dn)
        self.logger.debug("changed attributes: %r", self.diff(old, new))
        self._send_message(new, old)

    def remove(self, dn, old):
        self.logger.info("[ remove ] dn: %r", dn)
        self._send_message({}, old)

    def _ensure_queue_exists(self) -> None:
        try:
            asyncio.run(self._async_ensure_queue_exists())
        except OSError as exc:
            self.logger.error("Failed to connect to the message queue: %s", exc)
            raise

    async def _async_ensure_queue_exists(self) -> None:
        exception = None
        for attempt in range(self.settings.nats_max_retry_count + 1):
            if attempt != 0:
                time.sleep(self.settings.nats_retry_delay)
            try:
                async with self.mq as mq:
                    await mq.ensure_queue_exists()
                return
            except Exception as error:
                self.logger.error("Failed to ensure the NATS queue exists: %r, retries: %d", error, attempt)
                exception = error
        raise exception

    def _send_message(self, new, old) -> None:
        try:
            asyncio.run(self._async_send_message(new, old))
        except Exception as error:
            self.logger.error("Failed to send the LDAP message to NATS: %r", error)
            traceback.print_exc()
            self.kill_listener_process()
            raise

    async def _async_send_message(self, new, old) -> None:
        exception = None
        for attempt in range(self.settings.nats_max_retry_count + 1):
            if attempt != 0:
                time.sleep(self.settings.nats_retry_delay)
            try:
                async with self.mq as mq:
                    await mq.enqueue_change_event(new, old)
                    return
            except Exception as error:
                self.logger.error("Failed to send the LDAP message to NATS: %r, retries: %d", error, attempt)
                exception = error
        raise exception

    def kill_listener_process(self) -> None:
        """
        Kill the listener parent process
        """
        if not self.settings.terminate_listener_on_exception:
            self.logger.info(
                "Nubus provisioning listener failure is configured to not terminate the listener process. "
            )
            return
        process_name = "univention-directory-listener"

        self.logger.info(
            "Manually killing the listener parent process because the listener module encountered an exception"
        )
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if process_name in proc.info["name"]:
                    os.kill(proc.info["pid"], signal.SIGKILL)
            except (psutil.NoSuchProcess, psutil.AccessDenied, ProcessLookupError) as error:
                self.logger.error("Failed to kill the parent process %r", error)
                # Process may have already terminated or we don't have permission
                continue
