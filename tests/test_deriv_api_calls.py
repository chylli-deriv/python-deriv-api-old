import asyncio
import pytest
from deriv_api import deriv_api_calls

@pytest.mark.asyncio
async def test_deriv_api_calls(mocker):
    api = deriv_api_calls.DerivAPICalls()
    assert(isinstance(api, deriv_api_calls.DerivAPICalls))
    assert (await api.accountClosure("hello"))['needsMethodArg'] == '1'
    mocker.patch('deriv_api.deriv_api_calls.validateArgs', return_value='bad' )
    with pytest.raises(ValueError, match='bad'):
        await api.accountClosure("hello")
