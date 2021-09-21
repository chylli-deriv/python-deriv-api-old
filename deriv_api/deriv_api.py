#from deriv_api.deriv_api_calls import DerivAPICalls
import asyncio
import websockets
import json
import logging

# TODO: remove after development
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG
)

#class DerivAPI(DerivAPICalls):

class DerivAPI:
    """Main class of the python DerivAPI module. It provides methods to connect, read and interact with API"""
    wsconnection = ''

    def __init__(self, app_id, endpoint = 'frontend.binaryws.com', lang = 'EN', brand = ''):
        connectionArgument = {
            'app_id': str(app_id),
            'endpoint': endpoint,
            'lang': lang,
            'brand': brand
        }

        self.__set_apiURL(connectionArgument)
        self.apiconnect()

    def __set_apiURL(self, connectionArgument):
        self.api_url = "wss://ws.binaryws.com/websockets/v3?app_id="+connectionArgument['app_id']+"&l="+connectionArgument['lang']+"&brand="+connectionArgument['brand']

    def __get_apiURL(self):
        return self.api_url

    def apiconnect(self):
        if (self.wsconnection):
            return self.wsconnection
        else:
            self.wsconnection = websockets.connect(self.__get_apiURL)
            return 

    # this is called from client by api.buy, api.account... then in APICalls -> processRequest -> validateArgs + call this send
    async def send(self, message):
        loop.create_task(self.send_receive(message))

    async def send_receive(self, message):
        async with self.apiconnect() as websocket:
            await (websocket.send(json.dumps(message)))
            async for message in websocket:
                return self.parse(message)

    def parse(self, message):
        data = json.loads(message)
        if 'error' in data.keys():
            return 'error'
        return data

    #def add_api_call(self, request):
    #    loop.create_task(self.send_receive(request))

loop = asyncio.get_event_loop()
# connect & ping parallely
#loop.create_task(apiconnect())
loop.run_forever()
