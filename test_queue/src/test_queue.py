# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
import signal

from univention.admin.rest.client import UDM
from univention.provisioning.models.message import Message

from .config import Settings, settings
from .task_runner import Context, TaskRunner


class QueueContext(Context):
    def __init__(self, udm_task_callback, subscription_message_handler):
        Context.__init__(self, udm_task_callback, subscription_message_handler)
        self.received_create_users: list[str] = []


async def udm(context: Context, config: Settings, udm: UDM) -> None:
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
        udm_obj = module.new()
        udm_obj.properties.update(properties)
        udm_obj.save()

        context.created_users.append(udm_obj.dn)
        await asyncio.sleep(5)


async def handle_message(context: QueueContext, config: Settings, message: Message):
    if message.body.new and not message.body.old:
        print(f"Received user: {message.body.new['id']}")
        context.received_create_users.append(message.body.new["dn"])


async def shutdown(sig, context: QueueContext):
    print(f"Caught signal: {sig.name}")
    for task in context.tasks:
        task.cancel()

    await asyncio.gather(*context.tasks, return_exceptions=True)
    print("Shutdown complete.")


async def run():
    config = settings()
    context = QueueContext(udm, handle_message)
    task_runner = TaskRunner(context, config)

    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, context)))

    await task_runner.run()

    if context.created_users == context.received_create_users:
        print("SUCCESS: All created users where received via provisioning")
    else:
        print("FAILURE: Some created users where not received via provisioning")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
