#
from deriv_api import deriv_api
def test_hello():
    assert deriv_api.deriv_api(123, "connectionstr").hello() == "Hello world!"