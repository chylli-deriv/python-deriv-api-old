import asyncio

import pytest
from deriv_api.custom_future import CustomFuture
from asyncio.exceptions import InvalidStateError, CancelledError
def test_custom_future():
    f1 = CustomFuture()
    assert f1.is_pending()
    f1.set_result("hello")
    assert f1.result() == "hello"
    assert f1.is_resolved()
    with pytest.raises(InvalidStateError, match="invalid state"):
        f1.set_exception("world")
    f2 = CustomFuture()
    f2.set_exception(Exception)
    assert f2.is_rejected()

@pytest.mark.asyncio
async def test_wrap():
    # test resolved
    f1 = asyncio.Future()
    f2 = CustomFuture.wrap(f1)
    assert isinstance(f2, CustomFuture)
    assert f1.get_loop() is f2.get_loop()
    assert f2.is_pending()
    f1.set_result("hello")
    await f2
    assert f2.result() == "hello"
    assert f2.done()

    # test reject
    f1 = asyncio.Future()
    f2 = CustomFuture.wrap(f1)
    f1.set_exception(Exception("hello"))
    with pytest.raises(Exception, match='hello'):
        await f2
    assert f2.done()
    assert f2.is_rejected()

    # test cancel
    f1 = asyncio.Future()
    f2 = CustomFuture.wrap(f1)
    f1.cancel("hello")
    with pytest.raises(CancelledError, match='hello'):
        await f2
    assert f2.done()
    assert f2.is_cancelled()

@pytest.mark.asyncio
async def test_future_then():
    # test upstream ok
    # test callback future ok
    f1 = CustomFuture()
    def then_callback(last_result):
        f = CustomFuture()
        f.set_result(f"result: {last_result}")
        return f
    f2 = f1.then(then_callback)
    f1.set_result("f1 ok")
    assert (await f2) == 'result: f1 ok', "if inside future has result, then_future will has result too"

    # test callback fail
    f1 = CustomFuture()
    def then_callback(last_result):
        f = CustomFuture()
        f.set_exception(Exception(f"result: {last_result}"))
        return f

    f2 = f1.then(then_callback)
    f1.set_result("f1 ok")
    with pytest.raises(Exception, match='result: f1 ok'):
        await f2

    # test callback fail
    f1 = CustomFuture()

    def then_callback(last_result):
        f = CustomFuture()
        f.set_exception(Exception(f"result: {last_result}"))
        return f

    f2 = f1.then(then_callback)
    f1.set_result("f1 ok")
    with pytest.raises(Exception, match='result: f1 ok'):
        await f2

    # test upstream fail
    # test inside future ok
    f1 = CustomFuture()
    result = None

    def else_callback(last_exception: Exception):
        f = CustomFuture()
        f.set_result(f"f1 exception {last_exception.args[0]}")
        return f

    f2 = f1.then(None, else_callback)
    f1.set_exception(Exception("f1 bad"))
    assert (await f2) == 'f1 exception f1 bad'

    # test inside future exception
    f1 = CustomFuture()
    result = None

    def else_callback(last_exception: Exception):
        f = CustomFuture()
        f.set_exception(Exception(f"f1 exception {last_exception.args[0]}"))
        return f

    f2 = f1.then(None, else_callback)
    f1.set_exception(Exception("f1 bad"))
    with pytest.raises(Exception, match='f1 exception f1 bad'):
        await f2

    # upstream canceled
    f1 = CustomFuture()

    def else_callback(last_exception: Exception):
        f = CustomFuture()
        f.set_exception(Exception(f"f1 exception {last_exception.args[0]}"))
        return f

    f2 = f1.then(None, else_callback)
    f1.cancel('f1 cancelled')
    with pytest.raises(asyncio.exceptions.CancelledError, match='Upstream future cancelled'):
        await f2

