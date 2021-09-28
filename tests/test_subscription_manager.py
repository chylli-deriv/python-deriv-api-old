from deriv_api.subscription_manager import *

class API:
    pass

def test_get_msg_type():
    assert get_msg_type({'hello': 1}) is None
    assert get_msg_type({'proposal': 1}) == 'proposal'

def test_get_source():
    manager = SubscriptionManager(API())


