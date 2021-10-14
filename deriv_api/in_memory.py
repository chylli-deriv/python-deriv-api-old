
class InMemory:
    """An in memory storage which can be used for caching"""

    def __init__(self):
        self.store = {}
        self.type_store = {}

    def has(self, key):
        return key in self.store

    # we should serialize key (utils/dict_to_cache_key) before we store it
    # At first I want to use it directly here.
    # But from js version of deriv-api logic, user can choose cache object freely.
    # So we shouldn't suppose other cache module will serialize the key.
    # So we should always call serialize in the caller module
    def get(self, key):
        return self.store[key]

    def get_by_msg_type(self, msg_type):
        print(f"msg type is {msg_type}")
        return self.type_store.get(msg_type)

    def set(self, key, value):
        self.store[key] = value
        self.type_store[value['msg_type']] = value