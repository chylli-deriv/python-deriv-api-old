import pytest
import pytest_mock
from deriv_api import deriv_api
from deriv_api.errors import APIError, ConstructionError

def test_deriv_api(mocker):
    with pytest.raises(ConstructionError, match=r"An app_id is required to connect to the API"):
        deriv_api_obj = deriv_api.DerivAPI({'endpoint': 5432})

    with pytest.raises(ConstructionError, match=r"Endpoint must be a string, passed: <class 'int'>"):
        deriv_api_obj = deriv_api.DerivAPI({'app_id': 1234, 'endpoint': 5432})

    with pytest.raises(ConstructionError, match=r"Invalid URL:local123host"):
        deriv_api_obj = deriv_api.DerivAPI({'app_id': 1234, 'endpoint': 'local123host'})

    mocker.patch('deriv_api.deriv_api.DerivAPI.api_connect', return_value='')
    deriv_api_obj = deriv_api.DerivAPI({'app_id': 1234, 'endpoint': 'localhost'})
    assert(isinstance(deriv_api_obj, deriv_api.DerivAPI))

    message = '{"echo_req": {"ping": 1}, "msg_type": "ping", "ping": "pong"}'
    data = deriv_api_obj.parse_response(message)
    assert data['ping'] == 'pong'
    assert data['msg_type'] == 'ping'

    message='{"echo_req": {"active_symbols": "brief","product_type1": "basic"}, "error": {"code": "InputValidationFailed","details": {},"message": "Input validation failed: Properties not allowed: product_type1."},"msg_type": "active_symbols"}'
    data = deriv_api_obj.parse_response(message)
    assert data['error']['code'] == 'InputValidationFailed'