# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
import signal

import requests

from univention.admin.rest.client import UDM
from univention.provisioning.models.message import Message

from .config import Settings, settings
from .task_runner import Context, TaskRunner


class QueueContext(Context):
    def __init__(self, udm_task_callback, subscription_message_handler):
        Context.__init__(self, udm_task_callback, subscription_message_handler)
        self.received_users: list[str] = []
        self.changd_users: list[str] = []


async def udm(context: Context, config: Settings, udm: UDM) -> None:
    extended_attributes = []
    try:
        module = udm.get("users/user")
        for x in range(5):
            name = f"test-{len(context.created_users) + 1}"
            print(f"Create user: {name}")
            properties = {
                "username": name,
                "firstname": "John",
                "lastname": "Doe",
                "password": "password",
                "pwdChangeNextLogin": True,
            }
            udm_obj = module.new()
            udm_obj.properties.update(properties)
            udm_obj.save()

            context.created_users.append(udm_obj.dn)

        while context.created_users != context.received_users:
            await asyncio.sleep(2)

        context.received_users.clear()

        module = udm.get("settings/extended_attribute")

        udm_obj = module.new(position=f"cn=custom attributes,cn=univention,{config.ldap_base_dn}")
        udm_obj.properties["name"] = "TestAttribute1"
        udm_obj.properties["CLIName"] = "testAttribute1"
        udm_obj.properties["module"] = ["users/user"]
        udm_obj.properties["default"] = ""
        udm_obj.properties["ldapMapping"] = "univentionFreeAttribute1"
        udm_obj.properties["objectClass"] = "univentionFreeAttributes"
        udm_obj.properties["shortDescription"] = "Test attribute"
        udm_obj.properties["multivalue"] = False
        udm_obj.properties["valueRequired"] = False
        udm_obj.properties["mayChange"] = True
        udm_obj.properties["doNotSearch"] = False
        udm_obj.properties["deleteObjectClass"] = False
        udm_obj.properties["overwriteTab"] = False
        udm_obj.properties["fullWidth"] = True

        udm_obj.save()

        extended_attributes.append(udm_obj.dn)

        # Update extended attrobutes to allow setting it
        print("Refreshing cache")
        headers = {"Accept": "application/json"}
        response = requests.get(
            config.udm_url.rstrip("/") + "/users/user/add",
            auth=(config.udm_username, config.udm_password),
            headers=headers,
        )
        if response.status_code == 200:
            print("Cache refreshed")
        else:
            print(f"FAILED: Refresh cache: {response.text}")

        module = udm.get("users/user")
        for user_dn in context.created_users:
            print(f"Change user: {user_dn}")
            udm_obj = module.get(user_dn)

            udm_obj.properties["testAttribute1"] = user_dn
            udm_obj.save()
            context.changd_users.append(udm_obj.dn)

        while context.changd_users != context.received_users:
            await asyncio.sleep(2)
    finally:
        print("Deleting extended attributes")
        module = udm.get("settings/extended_attribute")
        for dn in extended_attributes:
            obj = module.get(dn)
            obj.delete()

    shutdown(context)


async def handle_message(context: QueueContext, config: Settings, message: Message):
    if message.body.new and not message.body.old:
        print(f"Received create user: {message.body.new['id']}")
        if "testAttribute1" in message.body.new["properties"]:
            print("FAILED: Extended attribute already available")
        context.received_users.append(message.body.new["dn"])
    elif message.body.new and message.body.old:
        print(f"Received change user: {message.body.new['id']}")
        if (
            "testAttribute1" in message.body.old["properties"]
            or "testAttribute1" not in message.body.new["properties"]
            or message.body.new["properties"]["testAttribute1"] != message.body.new["dn"]
        ):
            print("FAILED: Extended attribute not in changed object")
        else:
            print(
                f"SUCCESS: New extended attribute is set correctly: {message.body.new['properties']['testAttribute1']}"
            )
        context.received_users.append(message.body.new["dn"])


def shutdown(context):
    for task in context.tasks:
        task.cancel()


async def on_signal(sig, context):
    print(f"Caught signal: {sig.name}")
    shutdown(context)

    await asyncio.gather(*context.tasks, return_exceptions=True)
    print("Shutdown complete.")


async def run():
    config = settings()
    context = QueueContext(udm, handle_message)
    task_runner = TaskRunner(context, config)

    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(on_signal(s, context)))

    try:
        await task_runner.run()
    except asyncio.CancelledError:
        pass


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
