from __future__ import annotations
from asyncio import Future
from asyncio import CancelledError
class CustomFuture(Future):
    def __init__(self, *, loop=None):
        self.state = 'pending'
        super().__init__(loop = loop)

    @classmethod
    def wrap(cls, future: Future) -> CustomFuture:
        if isinstance(future, cls):
            return future

        custom_future = cls(loop = future.get_loop())
        def done_callback(f: Future):
            try:
                result = f.result()
                custom_future.set_result(result)
            except CancelledError as err:
                custom_future.cancel(*(err.args))
            except BaseException as err:
                custom_future.set_exception(err)

        future.add_done_callback(done_callback)
        return custom_future

    def set_result(self, *args):
        self.state = 'resolved'
        return super().set_result(*args)

    def set_exception(self, *args):
        self.state = 'rejected'
        return super().set_exception(*args)

    def cancel(self, *msg):
        self.state = 'cancelled'
        return super().cancel(*msg)

    def is_pending(self) -> bool:
        return self.state == 'pending'

    def is_resolved(self) -> bool:
        return self.state == 'resolved'

    def is_rejected(self) -> bool:
        return self.state == 'rejected'

    def is_cancelled(self) -> bool:
        return self.cancelled()