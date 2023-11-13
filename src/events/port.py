from .adapters.mq_abstract_adapter import MQAbstractAdapter

import core.models

class MQlibPort:

    def __init__(self, mq_adapter: MQAbstractAdapter):
        self._mq_adapter = mq_adapter

    def add_message(self, message: core.models.Message):
        self._mq_adapter.add_message(message)