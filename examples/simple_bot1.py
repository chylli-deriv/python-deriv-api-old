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
    api = deriv_api.DerivAPI(app_id=app_id)

    response = await api.ping({'ping':1})
    if response['ping']:
        print(response['ping'])

    active_symbols = await api.active_symbols({"active_symbols": "brief", "product_type": "basic"})
    print(active_symbols)

    ''' Authorize '''
    authorize = await api.authorize(api_token)
    print(authorize)

    ''' Get Balance '''
    response = await api.balance()
    response = response['balance']
    currency = response['currency']
    print("Your current balance is", response['currency'], response['balance'])

    # TODO test cache without fetch active_symbols directly
    # test cache after fetch cache directly
    # test cache with fetch active_symbols directly
    '''Get active symbols from cache'''
    cached_active_symbols = await api.cache.active_symbols({"active_symbols": "brief", "product_type": "basic"})
    print(cached_active_symbols)

    ''' get assets '''
    assets = await api.cache.asset_index({"asset_index": 1})
    print(assets)

    ''' Get proposal '''
    proposal = await api.proposal({"proposal": 1, "amount": 100, "barrier": "+0.1", "basis": "payout",
                                   "contract_type": "CALL", "currency": "USD", "duration": 60, "duration_unit": "s",
                                   "symbol": "R_100" ,
                                   #"subscribe":1
                                   })
    print(proposal)

    ''' Buy '''
    response = await api.buy({"buy": proposal.get('proposal').get('id'), "price": 100})
    print(response)
    print(response.get('buy').get('buy_price'))
    print(response.get('buy').get('contract_id'))
    print(response.get('buy').get('longcode'))

    ''' open contracts '''
    poc = await api.proposal_open_contract({"proposal_open_contract": 1, "contract_id": response.get('buy').get('contract_id'),
                                      #"subscribe": 1
                                      })
    print(poc)

    if not poc.get('proposal_open_contract').get('is_sold'):
        ''' sell '''
        sell = await api.sell({"sell": response.get('buy').get('contract_id'), "price": 80})
        print(sell)

    ''' profit table '''
    profit_table = await api.profit_table({"profit_table": 1, "description": 1, "sort": "ASC"})
    print(profit_table)

    ''' transaction statement '''
    statement = await api.statement({"statement": 1,"description": 1,"limit": 100,"offset": 25})
    print(statement)

    await api.disconnect()
    await api.clear()

asyncio.run(sample_calls())
