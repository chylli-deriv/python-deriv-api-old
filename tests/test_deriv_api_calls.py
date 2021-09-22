import asyncio
import pytest
from deriv_api import deriv_api_calls

@pytest.mark.asyncio
async def test_deriv_api_calls(mocker):
    api = deriv_api_calls.DerivAPICalls()
    assert isinstance(api, deriv_api_calls.DerivAPICalls)
    assert (await api.accountClosure({"hello": "world"}))["hello"] == 'world', 'accountClosure can get right result'
    mocker.patch('deriv_api.deriv_api_calls.validateArgs', return_value='bad' )
    with pytest.raises(ValueError, match='bad'):
        await api.accountClosure("hello")

def test_parse_validateArgs():
    assert deriv_api_calls.parseArgs({'config': {}, 'args': 'aArg', 'method': 'aMethod', 'needsMethodArg': 1})['aMethod'] == 'aArg', "method will be a key and arg will be value if arg is not a dict and needsMethodArg is true"