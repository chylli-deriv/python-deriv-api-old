from deriv_api.deriv_api_calls import DerivAPICalls
import pytest
import pytest_mock
from deriv_api import deriv_api

#deriv_api_obj = deriv_api.DerivAPI(1089)

def test_deriv_api(mocker):
    mocker.patch('deriv_api.apiconnect', return_value='')
    deriv_api_obj = deriv_api.DerivAPI(1234)
    assert(isinstance(deriv_api_obj, deriv_api.DerivAPI))