from deriv_api.cache import Cache
from deriv_api.deriv_api_calls import DerivAPICalls
from deriv_api.in_memory import InMemory
import websockets
import json
import logging
from deriv_api.errors import APIError, ConstructionError

# TODO: remove after development
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.ERROR
)

class DerivAPI(DerivAPICalls):
    """
    The minimum functionality provided by DerivAPI, provides direct calls to the API.
    `api.cache` is available if you want to use the cached data

    example
    apiFromEndpoint = deriv_api.DerivAPI({ endpoint: 'ws.binaryws.com', app_id: 1234 });

    param {Object}     options
    param {WebSocket=} options.connection - A ready to use connection
    param {String}     options.endpoint   - API server to connect to
    param {Number}     options.app_id     - Application ID of the API user
    param {String}     options.lang       - Language of the API communication
    param {String}     options.brand      - Brand name
    param {Object}     options.middleware - A middleware to call on certain API actions
    """
    wsconnection:str = ''
    storage = ''
    def __init__(self, options):
        if not options.get('app_id'):
            raise APIError('An app_id is required to connect to the API')

        endpoint = options.get('endpoint', 'frontend.binaryws.com')
        lang = options.get('lang', 'EN')
        brand = options.get('brand', '')
        cache = options.get('cache', InMemory())
        storage = options.get('storage')

        connection_argument = {
            'app_id': str(options.get('app_id')),
            'endpoint': endpoint,
            'lang': lang,
            'brand': brand
        }

        self.shouldReconnect = True
        self.__set_apiURL(connection_argument)

        if storage:
            self.storage = Cache(self, storage)

        self.cache = Cache(self.storage if self.storage else self, cache)

    def __set_apiURL(self, connection_argument):
        self.api_url = "wss://ws.binaryws.com/websockets/v3?app_id="+connection_argument['app_id']+"&l="+connection_argument['lang']+"&brand="+connection_argument['brand']

    def __get_apiURL(self):
        return self.api_url

    async def api_connect(self):
        print("api_connect")
        if not self.wsconnection:
            print("inside api_connect")
            self.wsconnection = await websockets.connect(self.api_url)
        return self.wsconnection

    async def send(self, message):
        try:
            response = await self.send_receive(message)
        except websockets.ConnectionClosed:
            if not self.shouldReconnect:
               return APIError("API Connection Closed")
            else:
                self.wsconnection = ''
                await self.api_connect()
                response = await self.send_receive(message)
        except websockets.ConnectionClosedError:
            self.wsconnection = ''
            await self.api_connect()
            response = await self.send_receive(message)

        await self.cache.set(message, response)
        if self.storage:
            self.storage.set(message, response)
        return response

    async def send_receive(self, message):
        if await self.cache.get_by_msg_type(message):
            value = await self.cache.get_by_msg_type(message)
            if not value and self.storage and self.storage.get_by_msg_type(message):
                return self.storage.get_by_msg_type(message)
            else:
                return value

        websocket = await self.api_connect()
        await websocket.send(json.dumps(message))
        async for response in websocket:
            if response is None:
                self.wsconnection = ''
                await self.send_receive()
            return self.parse_response(response)
   
    def parse_response(self, message):
        data = json.loads(message)
        return data

    async def disconnect(self):
        print("disconnecting")
        self.shouldReconnect = False
        await self.wsconnection.close()
