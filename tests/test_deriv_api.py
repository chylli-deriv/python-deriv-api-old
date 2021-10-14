import asyncio

import pytest
import pytest_mock
from deriv_api import deriv_api
from deriv_api.errors import APIError, ConstructionError
from deriv_api.custom_future import CustomFuture

def test_connect_parameter():
    with pytest.raises(ConstructionError, match=r"An app_id is required to connect to the API"):
        deriv_api_obj = deriv_api.DerivAPI(endpoint=5432)

    with pytest.raises(ConstructionError, match=r"Endpoint must be a string, passed: <class 'int'>"):
        deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint=5432)

    with pytest.raises(ConstructionError, match=r"Invalid URL:local123host"):
        deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint='local123host')

@pytest.mark.asyncio
async def test_deriv_api(mocker):
    mocker.patch('deriv_api.deriv_api.DerivAPI.api_connect', return_value='')
    deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint='localhost')
    assert(isinstance(deriv_api_obj, deriv_api.DerivAPI))
    await deriv_api_obj.clear()

@pytest.mark.asyncio
async def test_get_url(mocker):
    deriv_api_obj = get_deriv_api(mocker)
    assert deriv_api_obj.get_url("localhost") == "wss://localhost"
    assert deriv_api_obj.get_url("ws://localhost") == "ws://localhost"
    with pytest.raises(ConstructionError, match=r"Invalid URL:testurl"):
        deriv_api_obj.get_url("testurl")
    await deriv_api_obj.clear()

def get_deriv_api(mocker):
    mocker.patch('deriv_api.deriv_api.DerivAPI.api_connect', return_value=CustomFuture().set_result(1))
    deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint='localhost')
    return deriv_api_obj

@pytest.mark.asyncio
async def test_transform_none_to_future():
    loop = asyncio.get_event_loop()
    f = loop.create_future()
    trans_f = deriv_api.transform_none_to_future(f)
    f.set_result(True)
    await asyncio.sleep(0.01)
    assert trans_f.is_resolved()
    f = loop.create_future()
    trans_f = deriv_api.transform_none_to_future(f)
    f.set_result(None)
    await asyncio.sleep(0.01)
    assert trans_f.is_pending()