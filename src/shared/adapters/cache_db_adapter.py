class CacheDbAdapter:
    def __init__(self):
        pass

    def retrieve_old_obj(self):
        raise NotImplementedError

    def store_old_obj(self):
        raise NotImplementedError
