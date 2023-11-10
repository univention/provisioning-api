import core.models

class MQlibPort:

    def __init__(self, adapter: MQAbstractAdapter):
        self._adapter = adapter

    def add_message(self, message: core.models.Message):
        self._adapter.add_message(message)