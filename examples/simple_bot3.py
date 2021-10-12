# run it like PYTHONPATH=. python3 examples/simple_bot1.py
import sys
import asyncio
import os
from deriv_api import deriv_api
from rx import Observable
app_id = 1089


async def sample_calls():
    api = deriv_api.DerivAPI(app_id=app_id)
    source_tick_50: Observable  = await api.subscribe({'ticks': 'R_50'})
    print(f"source tick50 is {id(source_tick_50)}")
    source_tick_50.subscribe(lambda data: print(f"get R50 {data}"))
    await asyncio.sleep(5)
    await api.clear()

asyncio.run(sample_calls())
