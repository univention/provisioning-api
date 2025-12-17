# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
import os

from aiohttp.client_exceptions import ClientConnectorError, ServerDisconnectedError

from univention.admin.rest.client import UDM
from univention.provisioning.consumer.api import (
    MessageHandler,
    MessageHandlerSettings,
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
    RealmTopic,
)

from .config import Settings


class Context:
    def __init__(self, udm_task_callback, subscription_message_handler):
        self.created_users: list[str] = []
        self.tasks: []
        self.udm_task_callback = udm_task_callback
        self.subscription_message_handler = subscription_message_handler


class PortForward:
    def __init__(self, namespace):
        self.process = None
        self.namespace = namespace

    async def __aenter__(self):
        await self.restart()

    async def restart(self):
        if self.running():
            return

        print("Start port forwarding")
        self.process = await asyncio.create_subprocess_exec(
            "kubectl",
            "-n",
            self.namespace,
            "port-forward",
            "service/nubus-provisioning-api",
            "20080:http",
            stdout=asyncio.subprocess.PIPE,
            preexec_fn=lambda: os.setpgrp(),
        )

        print("Wait for port forwarding")
        while True:
            line = await self.process.stdout.readline()
            if not line:
                break

            if line.decode("utf-8").startswith("Forwarding from"):
                break

        print("Port forwarding successfully setup")

    def running(self):
        return self.process is not None and self.process.returncode is None

    async def __aexit__(self, type, value, traceback):
        if self.running():
            print("Close port forwarding")
            self.process.terminate()
            await self.process.wait()


class TaskRunner:
    def __init__(self, context: Context, config: Settings):
        self.context = context
        self.config = config
        self.tasks = []

    async def run(self):
        self.context.tasks = [asyncio.create_task(self.consumer()), asyncio.create_task(self.udm())]
        await asyncio.gather(*self.context.tasks)

    async def udm(self) -> None:
        await asyncio.sleep(5)
        try:
            udm = UDM.http(self.config.udm_url.rstrip("/") + "/", self.config.udm_username, self.config.udm_password)

            await self.context.udm_task_callback(self.context, self.config, udm)
        except asyncio.CancelledError:
            print("UDM task canceled")
        finally:
            print("Delete users")
            mod = udm.get("users/user")
            for dn in self.context.created_users:
                obj = mod.get(dn)
                obj.delete()

    async def consumer(self) -> None:
        subscriber_name = "test-queue"
        subscriber_password = "test-queue"

        admin_client_setting = ProvisioningConsumerClientSettings(
            provisioning_api_base_url=self.config.provisioning_api_base_url,
            provisioning_api_username=self.config.provisioning_api_username,
            provisioning_api_password=self.config.provisioning_api_password,
            log_level=self.config.log_level,
        )

        async with PortForward(self.config.kubernetes_namespace) as port_forward:
            async with ProvisioningConsumerClient(admin_client_setting) as admin_client:
                try:
                    print("Create subscription")
                    await admin_client.create_subscription(
                        name=subscriber_name,
                        password=subscriber_password,
                        realms_topics=[RealmTopic(realm="udm", topic="users/user")],
                        request_prefill=False,
                    )

                    client_settings = ProvisioningConsumerClientSettings(
                        provisioning_api_base_url=self.config.provisioning_api_base_url,
                        provisioning_api_username=subscriber_name,
                        provisioning_api_password=subscriber_password,
                        log_level=self.config.log_level,
                    )

                    message_handler_settings = MessageHandlerSettings(max_acknowledgement_retries=5)

                    # During restarts of the pods it can happen, that we loose the connection so just always retry in case of ServerDisconnectedError
                    while True:
                        try:
                            async with ProvisioningConsumerClient(client_settings) as client:
                                print("Wait for messages")
                                await MessageHandler(
                                    client,
                                    [
                                        lambda message: self.context.subscription_message_handler(
                                            self.context, self.config, message
                                        )
                                    ],
                                    message_handler_settings,
                                ).run()
                        except ServerDisconnectedError:
                            print("Disconnected from server, will retry in 5s")
                            await asyncio.sleep(5)
                        except ClientConnectorError as e:
                            if port_forward and not port_forward.running():
                                print("Failed to connect, redo the kubectl port forwarding and retry in 5s")
                                port_forward.restart()
                                await asyncio.sleep(5)
                            else:
                                raise e
                except asyncio.CancelledError:
                    print("Consumer task canceled")
                finally:
                    print("Delete subscription")
                    await admin_client.cancel_subscription(subscriber_name)
