import websockets
import json
import asyncio
import logging

# This works in local box (with python 3.9.6 websockets 9.1) not in this container. Need to check
# TODO: remove after development
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG
)

app_id = '1089'  # replace with your app_id.

async def apiconnect():
    uri = "wss://ws.binaryws.com/websockets/v3?app_id="+app_id

    async with websockets.connect(uri) as websocket:
        
       loop.create_task(ping(websocket))
        
    async for message in websocket: 
        data = json.loads(message)
        print('Data: %s' % message) #uncomment this line to see all response data.
        if 'error' in data.keys():
            print('Error Happened: %s' % message)

async def ping(ws):
    json_data = json.dumps({"ping": 1})
    while 1:
        await ws.send(json_data)
        await asyncio.sleep(10)

loop = asyncio.get_event_loop()
loop.create_task(apiconnect())
loop.run_forever()