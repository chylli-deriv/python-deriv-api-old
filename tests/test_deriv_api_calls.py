from deriv_api import deriv_api_calls

def test_deriv_api_calls():
    api = deriv_api_calls.DerivAPICalls()
    assert(isinstance(api, deriv_api_calls.DerivAPICalls))