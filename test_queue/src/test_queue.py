# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
import signal
import subprocess

from aiohttp.client_exceptions import ClientConnectorError, ServerDisconnectedError

from univention.admin.rest.client import UDM
from univention.provisioning.consumer.api import (
    MessageHandler,
    MessageHandlerSettings,
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
    RealmTopic,
)
from univention.provisioning.models.message import Message

from .config import Settings, settings


class Context:
    created_users: list[str] = []
    received_create_users: list[str] = []


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


async def udm(config: Settings, context: Context) -> None:
    await asyncio.sleep(5)
    try:
        udm = UDM.http(config.udm_url.rstrip("/") + "/", config.udm_username, config.udm_password)

        while True:
            name = f"test-{len(context.created_users) + 1}"
            print(f"Create user: {name}")
            properties = {
                "username": name,
                "firstname": "John",
                "lastname": "Doe",
                "password": "password",
                "pwdChangeNextLogin": True,
            }
            module = udm.get("users/user")
            object = module.new()
            object.properties.update(properties)
            object.save()

            context.created_users.append(object.dn)
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("UDM task cancelled")
    finally:
        print("Delete users")
        for dn in context.created_users:
            mod = udm.get("users/user")
            obj = mod.get(dn)
            obj.delete()


async def consumer(config: Settings, context: Context) -> None:
    subscriber_name = "test-queue"
    subscriber_password = "test-queue"

    admin_client_setting = ProvisioningConsumerClientSettings(
        provisioning_api_base_url=config.provisioning_api_base_url,
        provisioning_api_username=config.provisioning_api_username,
        provisioning_api_password=config.provisioning_api_password,
        log_level=config.log_level,
    )

    async with PortForward(config.kubernetes_namespace) as port_forward:
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
                    provisioning_api_base_url=config.provisioning_api_base_url,
                    provisioning_api_username=subscriber_name,
                    provisioning_api_password=subscriber_password,
                    log_level=config.log_level,
                )

                message_handler_settings = MessageHandlerSettings(max_acknowledgement_retries=5)

                # During restarts of the pods it can happen, that we loose the connection so just always retry in case of ServerDisconnectedError
                while True:
                    try:
                        async with ProvisioningConsumerClient(client_settings) as client:
                            print("Wait for messages")
                            await MessageHandler(
                                client, [lambda message: handle_message(message, context)], message_handler_settings
                            ).run()
                    except ServerDisconnectedError:
                        print("Disconnected from server, will retry in 5s")
                        await asyncio.sleep(5)
                    except ClientConnectorError as e:
                        if not port_forward.running():
                            print("Failed to connect, redo the kubectl port forwarding and retry in 5s")
                            context.portforward_process = subprocess.Popen(
                                ["kubectl", "port-forward", "service/nubus-provisioning-api", "20080:http"]
                            )
                            await asyncio.sleep(5)
                        else:
                            raise e
            except asyncio.CancelledError:
                print("Consumer task cancelled")
            finally:
                print("Delete subscription")
                # Not sure why but this crashes with a ClientConnectorError
                # await admin_client.cancel_subscription(subscriber_name)


async def handle_message(message: Message, context: Context):
    if message.body.new and not message.body.old:
        print(f"Received user: {message.body.new['id']}")
        context.received_create_users.append(message.body.new["dn"])


async def shutdown(sig, tasks):
    print(f"Caught signal: {sig.name}")
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    print("Shutdown complete.")


async def run():
    config = settings()
    context = Context()

    tasks = [asyncio.create_task(consumer(config, context)), asyncio.create_task(udm(config, context))]
    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, tasks)))
    await asyncio.gather(*tasks)

    if context.created_users == context.received_create_users:
        print("SUCCESS: All created users where received via provisioning")
    else:
        print("FAILURE: Some created users where not received via provisioning")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
