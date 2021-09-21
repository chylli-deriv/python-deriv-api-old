import asyncio
from deriv_api import deriv_api

app_id=1089
api_token=''

async def sample_calls():
    api = deriv_api.DerivAPI({app_id: app_id})
    response = await api.ping({'ping':1})
    print(response)

sample_calls()