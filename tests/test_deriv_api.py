import asyncio
from websockets import imports
from deriv_api import deriv_api
import json
import pytest


deriv_api_obj = deriv_api.DerivAPI(1089)

def test_connection():
    assert(isinstance(deriv_api_obj, deriv_api.DerivAPI))

@pytest.mark.asyncio
async def test_send_receive():
    response = await deriv_api_obj.add_api_call({'ping': 1})
    assert response['ping'] == 'pong'
