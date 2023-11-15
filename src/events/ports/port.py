from shared.adapters.mq_abstract_adapter import MQAbstractAdapter
from shared.models import Message


class MQlibPort:
    def __init__(self, mq_adapter: MQAbstractAdapter):
        self._mq_adapter = mq_adapter

    def add__event_message(self, message: Message):
        self._mq_adapter.add_message(message)
