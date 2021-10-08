import asyncio

import pytest
from deriv_api.custom_future import CustomFuture
from asyncio.exceptions import InvalidStateError
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
    f1 = asyncio.Future()
    f2 = CustomFuture.wrap(f1)
    assert isinstance(f2, CustomFuture)
    assert f1.get_loop() is f2.get_loop()
    assert f2.is_pending()
    f1.set_result("hello")
    #f1.get_loop().run_until_complete(f1)
    await f2
    assert f2.result() == "hello"
    assert f2.done()

    f1 = asyncio.Future()
    f2 = CustomFuture.wrap(f1)
    f1.set_exception(Exception("hello"))
    with pytest.raises(Exception, match='hello'):
        await f2
    assert f2.done()
    assert f2.is_rejected()
