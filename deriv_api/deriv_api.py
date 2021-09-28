from deriv_api.cache import Cache
from deriv_api.deriv_api_calls import DerivAPICalls
from deriv_api.in_memory import InMemory
import websockets
import json
import logging

# TODO: remove after development
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG
)
class DerivAPI(DerivAPICalls):
    """Main class of the python DerivAPI module. It provides methods to connect, read and interact with API"""
    wsconnection:str = ''
    storage = ''
    def __init__(self, app_id, endpoint = 'frontend.binaryws.com', lang = 'EN', brand = '', cache = InMemory(), storage = ''):
        connection_argument = {
            'app_id': str(app_id),
            'endpoint': endpoint,
            'lang': lang,
            'brand': brand
        }

        self.__set_apiURL(connection_argument)

        if storage:
            self.storage = Cache(self, storage)

        self.cache = Cache(self.storage if self.storage else self, cache)


    def __set_apiURL(self, connection_argument):
        self.api_url = "wss://ws.binaryws.com/websockets/v3?app_id="+connection_argument['app_id']+"&l="+connection_argument['lang']+"&brand="+connection_argument['brand']

    def __get_apiURL(self):
        return self.api_url

    async def api_connect(self):
        print("connectinggggggggg")
        if not self.wsconnection:
            self.wsconnection = await websockets.connect(self.api_url)
            print(type(self.wsconnection))
        return self.wsconnection

    async def send(self, message):
        response = await self.send_receive(message)
        self.cache.set(message, response)
        if self.storage:
            self.storage.set(message, response)
        return response

    async def send_receive(self, message):
        websocket = await self.api_connect()
        await websocket.send(json.dumps(message))
        async for message in websocket:
            return self.parse_response(message)
   
    def parse_response(self, message):
        data = json.loads(message)
        return data