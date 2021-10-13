from __future__ import annotations
from asyncio import Future, CancelledError, InvalidStateError
from typing import Any, Optional, TypeVar, Union, Callable

_T = TypeVar("_T")
_S = TypeVar("_S")


class CustomFuture(Future):
    def __init__(self, *, loop=None, label=None) -> None:
        super().__init__(loop=loop)
        if not label:
            label = f"Future {id(self)}"
        self.label = label

    @classmethod
    def wrap(cls, future: Future) -> CustomFuture:
        if isinstance(future, cls):
            return future

        custom_future = cls(loop=future.get_loop())
        custom_future.cascade(future)
        return custom_future

    def resolve(self, *args: _T) -> None:
        return super().set_result(*args)

    def reject(self, *args: Union[type, BaseException]) -> None:
        return super().set_exception(*args)

    def is_pending(self) -> bool:
        return not self.done()

    def is_resolved(self) -> bool:
        return self.done() and not self.cancelled() and not self.exception()

    def is_rejected(self) -> bool:
        return self.done() and not self.cancelled() and self.exception()

    def is_cancelled(self) -> bool:
        return self.cancelled()

    def cascade(self, future: Future) -> CustomFuture:
        """copy another future result to itself"""
        if self.done():
            raise InvalidStateError('invalid state')

        def done_callback(f: Future) -> Callable[[_S], Any]:
            try:
                result = f.result()
                self.set_result(result)
            except CancelledError as err:
                self.cancel(*(err.args))
            except BaseException as err:
                self.set_exception(err)

        future.add_done_callback(done_callback)
        return self

    def then(self, then_callback: Callable[[_S], Any], else_callback=None) -> CustomFuture:
        new_future = CustomFuture(loop=self.get_loop())

        def done_callback(myself: CustomFuture) -> Callable[[_S], Any]:
            f: Optional[CustomFuture] = None
            if myself.is_cancelled():
                new_future.cancel('Upstream future cancelled')
                return

            if myself.is_rejected() and else_callback:
                f = else_callback(myself.exception())
            elif myself.is_resolved() and then_callback:
                f = then_callback(myself.result())

            if f is None:
                new_future.cascade(self)

            def inside_callback(internal_future: CustomFuture) -> Callable[[_S], Any] :
                new_future.cascade(internal_future)

            f.add_done_callback(inside_callback)

        self.add_done_callback(done_callback)
        return new_future

    def catch(self, else_callback: Callable[[_S], Any]):
        return self.then(None, else_callback)
