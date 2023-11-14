import core.models

class MQAbstractAdapter:

    def __init__(self):
        pass

    def add_message(self, message: core.models.Message):
        raise NotImplementedError