import asyncio
import pytest
from deriv_api import deriv_api_calls

@pytest.mark.asyncio
async def test_deriv_api_calls():
    api = deriv_api_calls.DerivAPICalls()
    assert(isinstance(api, deriv_api_calls.DerivAPICalls))
    assert (await api.accountClosure("hello"))['needsMethodArg'] == '1'