from .mq_abstract_adapter import MQAbstractAdapter

import core.models


class MQNatsAdapter(MQAbstractAdapter):

    def __init__(self):
        pass


    def add_message(self, message: core.models.Message):
        raise NotImplementedError