from ..models import Message


class MQAbstractAdapter:
    def __init__(self):
        pass

    def add_message(self, message: Message):
        raise NotImplementedError
