from .adapters.mq_abstract_adapter import MQAbstractAdapter

import core.models

class MQlibPort:

    def __init__(self):
        self._mq_adapter = MQAbstractAdapter() # do proper dependency injection here

    def add_message(self, message: core.models.Message):
        self._mq_adapter.add_message(message)