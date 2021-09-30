import sys
sys.path.append('.')
import asyncio
import os
from deriv_api import deriv_api

app_id = 1089
api_token = os.getenv('DERIV_TOKEN', '')

if len(api_token) == 0:
    sys.exit("DERIV_TOKEN environment variable is not set")

async def sample_calls():
    api = deriv_api.DerivAPI({'app_id': app_id})
    response = await api.ping({'ping':1})
    if response['ping']:
        print(response['ping'])

    active_symbols = await api.active_symbols({"active_symbols": "brief", "product_type": "basic"})
    print(active_symbols)

    '''Authorize'''
    authorize = await api.authorize(api_token)
    print(authorize)

    '''Get Balance'''
    response = await api.balance()
    response = response['balance']
    currency = response['currency']
    print("Your current balance is", response['currency'], response['balance'])

    '''Get active symbols from cache'''
    cached_active_symbols = await api.cache.active_symbols({"active_symbols": "brief", "product_type": "basic"})
    print(cached_active_symbols)



asyncio.run(sample_calls())
