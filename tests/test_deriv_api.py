import pytest_mock
from deriv_api import deriv_api

def test_deriv_api(mocker):
    mocker.patch('deriv_api.deriv_api.DerivAPI.apiconnect', return_value='')
    deriv_api_obj = deriv_api.DerivAPI(1234)
    assert(isinstance(deriv_api_obj, deriv_api.DerivAPI))
    
    message = '{"echo_req": {"ping": 1}, "msg_type": "ping", "ping": "pong"}'
    data = deriv_api_obj.parse_response(message)
    assert data['ping'] == 'pong'
    assert data['msg_type'] == 'ping'

    message='{"echo_req": {"active_symbols": "brief","product_type1": "basic"}, "error": {"code": "InputValidationFailed","details": {},"message": "Input validation failed: Properties not allowed: product_type1."},"msg_type": "active_symbols"}'
    data = deriv_api_obj.parse_response(message)
    assert data['error']['code'] == 'InputValidationFailed'
