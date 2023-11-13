from .mq_abstract_adapter import MQAbstractAdapter

class MQNatsAdapter(MQAbstractAdapter):

    def __init__(self):
        pass


    def add_message(self):
        raise NotImplementedError