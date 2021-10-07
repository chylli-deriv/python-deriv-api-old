import pytest

from deriv_api.subscription_manager import *
from rx.subject import Subject
from rx import Observable
import asyncio

mocked_response = {}

class API:
    def __init__(self):
        self.subject = Subject()
        self.mocked_response = {}
    async def send_and_get_source(self, request: dict) -> Subject:
        return self.subject
    def send(self, request: dict):
        return request
    async def emit(self):
        await asyncio.sleep(0.1)
        self.subject.on_next(self.mocked_response)


def test_get_msg_type():
    assert get_msg_type({'hello': 1}) is None
    assert get_msg_type({'proposal': 1}) == 'proposal'

@pytest.mark.asyncio
async def test_subscribe(mocker):
    api: API = API()
    subscription_manager = SubscriptionManager(api)
    api.mocked_response = {"msg_type": "proposal", 'subscription': {'id':'ID12345'}}
    assert not subscription_manager.source_exists({'proposal': 1}), "at start there is no such source"
    # get source first time
    source, emit = await asyncio.gather(subscription_manager.subscribe({'proposal': 1}), api.emit())
    assert isinstance(source, Observable)

    # get source second time
    source2, emit = await asyncio.gather(subscription_manager.subscribe({'proposal': 1}), api.emit())
    assert (source is source2), "same result"
    assert (source is subscription_manager.get_source({'proposal': 1})), 'source is in the cache'
    assert subscription_manager.source_exists({'proposal': 1}), "source in the cache"
    forget_result = subscription_manager.forget('ID12345')
    assert forget_result == {'forget': 'ID12345'}
    assert api.subject.is_disposed, "source is disposed"
