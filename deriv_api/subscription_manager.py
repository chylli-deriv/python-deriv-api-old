from deriv_api.utils import dict_to_cache_key
from deriv_api.errors import APIError

# streams_list is the list of subscriptions msg_types available.
# Please add / remove based on current available streams in api.
# Refer https: // developers.binary.com /
# TODO auto generate this one
streams_list = ['balance', 'candles', 'p2p_advertiser', 'p2p_order', 'proposal',
                'proposal_array', 'proposal_open_contract', 'ticks', 'ticks_history', 'transaction',
                'website_status']


class SubscriptionManager:
    def __init__(self, api):
        self.api = api
        self.sources = {}
        self.subs_id_to_key = {}
        self.key_to_subs_id = {}
        self.buy_key_to_contract_id = {}
        self.subs_per_msg_type = []


def get_msg_type(request):
    return next((x for x in streams_list if x in request), None)
