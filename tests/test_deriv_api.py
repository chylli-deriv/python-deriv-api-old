import asyncio

import pytest
import pytest_mock
from deriv_api import deriv_api
from deriv_api.errors import APIError, ConstructionError
from deriv_api.custom_future import CustomFuture
from rx.subject import Subject
import rx.operators as op
import pickle

class MockedWs:
    def __init__(self):
        self.data = []
        self.called = {'send': 0, 'recv' : 0}
        self.slept_at = 0
        self.queue = Subject()
        self.req_res_map = {}
        async def build_queue():
            while 1:
                await asyncio.sleep(0.01)
                # make queue
                data = self.data
                self.data = []
                for d in data:
                    await asyncio.sleep(0.01)
                    self.queue.on_next(d)
                    # if subscription, then we keep it
                    if d.get('subscription'):
                        self.data.append(d)
        self.task_build_queue = asyncio.create_task(build_queue())
    async def send(self, request):
        self.called['send'] += 1
        key = pickle.dumps(request)
        response = self.req_res_map.get(key)
        if response:
            self.data.append(response)
            self.req_res_map.pop(key)

    async def recv(self):
        self.called['recv'] += 1
        return await self.queue.pipe(op.first(),op.to_future())

    def add_data(self,response):
        key = pickle.dumps(response['echo_req'])
        self.req_res_map[key] = response

    def clear(self):
        self.task_build_queue.cancel('end')

def test_connect_parameter():
    with pytest.raises(ConstructionError, match=r"An app_id is required to connect to the API"):
        deriv_api_obj = deriv_api.DerivAPI(endpoint=5432)

    with pytest.raises(ConstructionError, match=r"Endpoint must be a string, passed: <class 'int'>"):
        deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint=5432)

    with pytest.raises(ConstructionError, match=r"Invalid URL:local123host"):
        deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint='local123host')

@pytest.mark.asyncio
async def test_deriv_api(mocker):
    mocker.patch('deriv_api.deriv_api.DerivAPI.api_connect', return_value='')
    deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint='localhost')
    assert(isinstance(deriv_api_obj, deriv_api.DerivAPI))
    await deriv_api_obj.clear()

@pytest.mark.asyncio
async def test_get_url(mocker):
    deriv_api_obj = get_deriv_api(mocker)
    assert deriv_api_obj.get_url("localhost") == "wss://localhost"
    assert deriv_api_obj.get_url("ws://localhost") == "ws://localhost"
    with pytest.raises(ConstructionError, match=r"Invalid URL:testurl"):
        deriv_api_obj.get_url("testurl")
    await deriv_api_obj.clear()

def get_deriv_api(mocker):
    mocker.patch('deriv_api.deriv_api.DerivAPI.api_connect', return_value=CustomFuture().set_result(1))
    deriv_api_obj = deriv_api.DerivAPI(app_id=1234, endpoint='localhost')
    return deriv_api_obj

@pytest.mark.asyncio
async def test_transform_none_to_future():
    loop = asyncio.get_event_loop()
    f = loop.create_future()
    trans_f = deriv_api.transform_none_to_future(f)
    f.set_result(True)
    await asyncio.sleep(0.01)
    assert trans_f.is_resolved()
    f = loop.create_future()
    trans_f = deriv_api.transform_none_to_future(f)
    f.set_result(None)
    await asyncio.sleep(0.01)
    assert trans_f.is_pending()

@pytest.mark.asyncio
async def test_mocked_ws():
    wsconnection = MockedWs()
    data1 = {"echo_req":{"ticks" : 'R_50'} ,"msg_type": "ticks", "subscription": {"id": "world"}}
    data2 = {"echo_req":{"ping": 1},"msg_type": "ping", "pong": 1}
    req_res = []
    wsconnection.add_data(data1)
    wsconnection.add_data(data2)
    await wsconnection.send(data1["echo_req"])
    await wsconnection.send(data2["echo_req"])
    assert await wsconnection.recv() == data1, "we can get first data"
    assert await wsconnection.recv() == data2, "we can get second data"
    assert await wsconnection.recv() == data1, "we can still get first data becaues it is a subscription"
    assert await wsconnection.recv() == data1, "we will not get second data because it is not a subscription"
    assert wsconnection.called['send'] == 2
    assert wsconnection.called['recv'] == 4
    wsconnection.clear()

@pytest.mark.asyncio
async def test_simple_send():
    wsconnection = MockedWs()
    api = deriv_api.DerivAPI(connection = wsconnection)
    data1 = {"echo_req":{"ping": 1},"msg_type": "ping", "pong": 1}
    wsconnection.add_data(data1)
    print(await api.send(data1['echo_req']))
