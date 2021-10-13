def error_factory(type: str) -> object:
    class GenericError(Exception):
        def __init__(self, message: str):
            super().__init__(message)
            self.type = type
            self.message = message

        def __str__(self) -> str:
            return f'{self.type}:{self.message}'

    return GenericError


class APIError(error_factory('APIError')):
    pass


class ConstructionError(error_factory('ConstructionError')):
    pass
