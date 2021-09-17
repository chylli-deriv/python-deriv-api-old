#
from deriv_api import deriv_api
import json

deriv_api_obj = deriv_api.deriv_api(1089)

#def test_connection():
#    json_data = json.dumps({'ping': 1})
#    deriv_api_obj.wsconnection.send(json_data)
#    deriv_api_obj.wsconnection.recv() == 'test'

def test_on_ping():
    expected = "test ping"
    assert deriv_api_obj.on_ping(deriv_api_obj.wsconnection, "test ping") == expected

def test_on_pong():
    expected = "pong"
    message = '{"echo_req": {"ping": 1}, "msg_type": "ping", "ping": "pong"}'
    assert deriv_api_obj.on_pong(deriv_api_obj.wsconnection, message) == expected

def test_on_message():
    message = '{"echo_req": {"ping": 1}, "msg_type": "ping", "ping": "pong"}'
    data = deriv_api_obj.on_message(deriv_api_obj.wsconnection, message)
    assert data['msg_type'] == "ping"
    assert data['ping'] == "pong"