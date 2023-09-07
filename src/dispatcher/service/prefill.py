from datetime import datetime
from typing import List, Tuple

import aiohttp
import core.models

from dispatcher.config import settings

from dispatcher.persistence.messages import MessageRepository
from dispatcher.persistence.redis import get_redis
from dispatcher.persistence.subscriptions import SubscriptionRepository
from dispatcher.service.messages import MessageService
from dispatcher.service.subscription import SubscriptionService


async def pre_fill_queue(subscriber_name: str, realms_topics: List[Tuple[str, str]]):
    async with get_redis() as redis:
        msg_repo = MessageRepository(redis)
        msg_service = MessageService(msg_repo)
        sub_repo = SubscriptionRepository(redis)
        sub_service = SubscriptionService(sub_repo)

        await sub_service.set_subscriber_queue_status(subscriber_name, core.models.FillQueueStatus.running)

        try:
            for realm, topic in realms_topics:
                if realm == "udm":
                    await pre_fill_udm(msg_service, subscriber_name, topic)
                else:
                    # FIXME: unhandled realm
                    pass
        except:
            await sub_service.set_subscriber_queue_status(subscriber_name, core.models.FillQueueStatus.failed)
        finally:
            await sub_service.set_subscriber_queue_status(subscriber_name, core.models.FillQueueStatus.done)


async def pre_fill_udm(service: MessageService, subscriber_name: str, topic: str):
    auth = aiohttp.BasicAuth(settings.udm_username, settings.udm_password)
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(f"{settings.udm_url}/") as request:
            pass
            # TODO
            this_topic = "TODO"
            pre_fill_udm_topic(service, subscriber_name, this_topic)


async def pre_fill_udm_topic(service: MessageService, subscriber_name: str, topic: str):
    auth = aiohttp.BasicAuth(settings.udm_username, settings.udm_password)
    async with aiohttp.ClientSession(auth=auth) as session:
        # Note: the size of the returned object is limited by the UCR variable
        # `directory/manager/web/sizelimit` in the UDM REST API container
        # (default: 400.000 bytes).
        #
        # We should probably use pagination to fetch the objects but the parameters
        # `page` and `limit` are marked as "Broken/Experimental" in the UDM REST API.
        params = {
            #"page": "1"
            #"limit": "100"
        }

        async with session.get(f"{settings.udm_url}/{topic}", params=params) as request:
            # TODO
            message = core.models.Message(
                publisher_name="udm-pre-fill",
                ts=datetime.now(),
                realm="udm",
                topic=topic,
                body={}, # TODO
            )
            await service.add_prefill_message(subscriber_name, message)
