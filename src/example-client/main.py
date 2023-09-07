#!/usr/bin/env python3
import argparse
import asyncio
from datetime import datetime
import uuid

import core.client


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="URL of the provisioning dispatcher")
    parser.add_argument("realm_topic", nargs="+", help="[realm]:[topic]")
    parser.add_argument(
        "--name", "-n", default=uuid.uuid4(), help="Name of the subscriber"
    )
    parser.add_argument("--fill", action="store_true", help="Fill the queue from LDAP")
    args = parser.parse_args()

    name = args.name
    realms_topics = [entry.split(":") for entry in args.realm_topic]

    client = core.client.AsyncClient(args.base_url)
    await client.create_subscription(name, realms_topics, args.fill)

    async with client.stream(name) as stream:
        message: core.client.Message = await stream.receive_message()
        print("<<<", datetime.now())
        print(message.model_dump_json(indent=2))

        print(">>>", datetime.now)
        status = core.client.MessageProcessingStatus.ok
        print(status)
        await stream.send_report(status)


if __name__ == "__main__":
    asyncio.run(main())
