class MessageService:

    def __init__(self, repo: MessageRepository):
        self._repo = repo