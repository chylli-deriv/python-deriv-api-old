import pytest
import re
from deriv_api import deriv_api_calls


@pytest.mark.asyncio
async def test_deriv_api_calls(mocker):
    api = deriv_api_calls.DerivAPICalls()
    assert isinstance(api, deriv_api_calls.DerivAPICalls)
    assert (await api.account_closure({'account_closure': 1, 'reason': 'want'})) == {'account_closure': 1,
                                                                                    'reason': 'want'}, 'account_closure can get right result'
    mocker.patch('deriv_api.deriv_api_calls.validate_args', return_value='bad')
    with pytest.raises(ValueError, match='bad'):
        await api.account_closure({})


def test_parse_parse_args():
    assert deriv_api_calls.parse_args(
        {'config': {'acc': {'type': 'boolean'}}, 'args': '1', 'method': 'acc', 'needsMethodArg': 1}) == {
               'acc': 1}, "method will be a key and arg will be value if arg is not a dict and needsMethodArg is true"
    assert deriv_api_calls.parse_args(
        {'config': {'acc': {'type': 'boolean'}}, 'args': {'acc': '0'}, 'method': 'acc', 'needsMethodArg': 1}) == {
               'acc': 0}, "method value will from args if arg is a dict and needsMethodArg is true"
    assert deriv_api_calls.parse_args({'config': {'acc': {'type': 'string'}}, 'args': {'hello': 0}, 'method': 'acc',
                                      'needsMethodArg': 1}) is None, "if arg is not in config, then return none"
    # test type
    assert deriv_api_calls.parse_args(
        {'config': {'acc': {'type': 'string'}}, 'args': {'acc': 0}, 'method': 'acc', 'needsMethodArg': 1}) == {
               'acc': '0'}, "arg is string"
    assert deriv_api_calls.parse_args(
        {'config': {'acc': {'type': 'numeric'}}, 'args': {'acc': '0'}, 'method': 'acc', 'needsMethodArg': 1}) == {
               'acc': 0}, "arg is numeric"
    assert deriv_api_calls.parse_args(
        {'config': {'acc': {'type': 'boolean'}}, 'args': {'acc': '0'}, 'method': 'acc', 'needsMethodArg': 1}) == {
               'acc': 0}, "arg is boolean"

def test_validate_args():
    assert re.match('Requires an dict',deriv_api_calls.validate_args({},""))
    assert deriv_api_calls.validate_args({'k1': {'required': 1}, 'k2': {}}, {'k1': 1, 'k2': 2, 'k3': 3}) == '', 'required keys are there'
    error_msg = deriv_api_calls.validate_args({'k1': {'required': 1}, 'k2': {'required': 1}}, {'k3': 1})
    assert re.search('k1', error_msg) and re.search('k2', error_msg), 'missed keys will be reported'
    config = {
        'k1': {'type': 'dict'},
        'k2': {'type': 'string'},
        'k3': {'type': 'numeric'},
        'k4': {'type': 'boolean'},
        'k5': {}
    }
    error_msg = deriv_api_calls.validate_args(config, {'k1': 1, 'k2': 1, 'k3': 'aString', 'k4': 'aString'})
    assert re.search("dict value expected but found <class 'int'>: k1 ", error_msg)
    assert re.search("string value expected but found <class 'int'>: k2", error_msg)
    assert re.search("numeric value expected but found <class 'str'>: k3", error_msg)
    assert re.search("boolean value expected but found <class 'str'>: k4", error_msg)
    error_msg = deriv_api_calls.validate_args(config, {'k1': {}, 'k2': "string", 'k3': 1, 'k4': True, 'k5': 1})
    assert error_msg == ''
