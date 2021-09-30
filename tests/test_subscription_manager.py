import asyncio

from deriv_api.subscription_manager import *
from rx.subject import Subject
import asyncio

loop = asyncio.get_event_loop()
class API:
    def send_and_get_source(self, request: dict) -> Subject:
        subject = Subject()
        subject.on_next({"msg_type": "proposal", 'subscription': {'id':'ID12345'}})

        return subject

def test_get_msg_type():
    assert get_msg_type({'hello': 1}) is None
    assert get_msg_type({'proposal': 1}) == 'proposal'

def test_subscribe():
    api: API = API()
    subscription_manager = SubscriptionManager(loop, api)
    source: Subject = subscription_manager.subscribe({'proposal': 1})
    assert isinstance(source, Subject)

