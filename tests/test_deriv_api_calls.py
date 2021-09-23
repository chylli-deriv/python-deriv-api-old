import asyncio
import pytest
from deriv_api import deriv_api_calls

@pytest.mark.asyncio
async def test_deriv_api_calls(mocker):
    api = deriv_api_calls.DerivAPICalls()
    assert isinstance(api, deriv_api_calls.DerivAPICalls)
    assert (await api.accountClosure({'account_closure': 1, 'reason': 'want'})) == {'account_closure': 1, 'reason': 'want'}, 'accountClosure can get right result'
    mocker.patch('deriv_api.deriv_api_calls.validateArgs', return_value='bad' )
    with pytest.raises(ValueError, match='bad'):
        await api.accountClosure({})

def test_parse_validateArgs():
    assert deriv_api_calls.parseArgs({'config': {'acc': {'type': 'boolean'}}, 'args': '1', 'method': 'acc', 'needsMethodArg': 1}) == {'acc': 1}, "method will be a key and arg will be value if arg is not a dict and needsMethodArg is true"
    assert deriv_api_calls.parseArgs({'config': {'acc': {'type': 'boolean'}}, 'args': {'acc': '0'}, 'method': 'acc', 'needsMethodArg': 1}) == {'acc': 0}, "method value will from args if arg is a dict and needsMethodArg is true"
    assert deriv_api_calls.parseArgs({'config': {'acc': {'type': 'string'}}, 'args': {'hello': 0}, 'method': 'acc', 'needsMethodArg': 1}) == None, "if arg is not in config, then return none"
    # test type
    assert deriv_api_calls.parseArgs({'config': {'acc': {'type': 'string'}}, 'args': {'acc': 0}, 'method': 'acc', 'needsMethodArg': 1}) == {'acc': '0'}, "arg is string"
    assert deriv_api_calls.parseArgs({'config': {'acc': {'type': 'numeric'}}, 'args': {'acc': '0'}, 'method': 'acc', 'needsMethodArg': 1}) == {'acc': 0}, "arg is numeric"
    assert deriv_api_calls.parseArgs({'config': {'acc': {'type': 'boolean'}}, 'args': {'acc': '0'}, 'method': 'acc', 'needsMethodArg': 1}) == {'acc': 0}, "arg is boolean"