from asyncio import Future
from asyncio import CancelledError
class CustomFuture(Future):
    def __init__(self, *args):
        self.state = 'pending'
        super().__init__(*args)
        return self

    @classmethod
    def wrap(cls, future: Future) -> CustomFuture:
        if isinstance(future, cls):
            return future

        custom_future = cls(loop = future.get_loop())
        def done_callback(f: Future):
            try:
                result = f.result()
                custom_future.set_result(result)
            except CancelledError:
                custom_future.cancel()
            except Exception as err:
                custom_future.set_exception(err)

        future.add_done_callback(done_callback)

    def set_result(self, *args):
        self.state = 'resolved'
        return super().set_result(*args)

    def set_exception(self, *args):
        self.state = 'rejected'
        return super().set_exception(*args)

    def is_pending(self) -> bool:
        return self.state == 'pending'

    def is_resolved(self) -> bool:
        return self.state == 'resolved'

    def is_rejected(self) -> bool:
        return self.state == 'rejected'
