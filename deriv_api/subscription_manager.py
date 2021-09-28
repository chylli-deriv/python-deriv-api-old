from deriv_api.utils import dict_to_cache_key
from deriv_api.errors import APIError
from rx import operators as op

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

    def subscribe(self, request):
        """
        Subscribe to a given request, returns a stream of new responses,
        Errors should be handled by the user of the stream

        example
        const ticks = api.subscribe({ 'ticks': 'R_100' });
        ticks.subscribe(log) // Print every new tick

        param {Object} request - A request object acceptable by the API

        returns {Observable} - An RxPY SObservable
        """
        if self.source_exists(request):
            return self.get_source(request)

        return self.create_new_source(request)

    def get_source(self, request):
        key = dict_to_cache_key(request)
        if key in self.sources:
            return self.sources[key]

        # if we have a buy subscription reuse that for poc
        for c in self.buy_key_to_contract_id.values():
            if c['contract_id'] == request['contract_id']:
                return self.sources[c['buy_key']]

        return None

    def source_exists(self, request):
        return self.get_source(request)

    def create_new_source(self, request):
        key = dict_to_cache_key(request)
        async def forget_old_source():
            if key not in self.key_to_subs_id:
                return
            try:
                self.forget(self.key_to_subs_id[key])
            except Exception:
                pass
        source = self.api.send_and_get_source(request).pipe(
            op.finally_action(forget_old_source),
            op.share()
        )

        self.sources[key] = source
        self.save_subs_per_msg_type(request, key)

        source.pipe(op.first(),op.to_future())

    def forget(self,id):
        pass

    # ...types
    def forget_all(self):
        pass

    def complete_subs_by_ids(self):
        pass

    def save_subs_id(self):
        pass

    def save_subs_per_msg_type(self):
        pass

    def remove_key_on_error(self):
        pass

    def complete_subs_by_key(self):
        pass

def get_msg_type(request):
    return next((x for x in streams_list if x in request), None)
