from deriv_api.cache import Cache
from deriv_api.deriv_api_calls import DerivAPICalls
from deriv_api.in_memory import InMemory
import websockets
import json
import logging
from deriv_api.errors import APIError, ConstructionError
from deriv_api.utils import dict_to_cache_key, is_valid_url
import re

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

    property {Cache} cache - Temporary cache default to {InMemory}
    property {Cache} storage - If specified, uses a more persistent cache (local storage, etc.)
    """
    wsconnection:str = ''
    storage = ''
    def __init__(self, options):
        if not options.get('app_id'):
            raise ConstructionError('An app_id is required to connect to the API')

        endpoint = options.get('endpoint', 'frontend.binaryws.com')
        lang = options.get('lang', 'EN')
        brand = options.get('brand', '')
        cache = options.get('cache', InMemory())
        storage = options.get('storage')

        connection_argument = {
            'app_id': str(options.get('app_id')),
            'endpoint_url': self.get_url(endpoint),
            'lang': lang,
            'brand': brand
        }

        self.shouldReconnect = True
        self.__set_apiURL(connection_argument)

        if storage:
            self.storage = Cache(self, storage)

        # If we have the storage look that one up
        self.cache = Cache(self.storage if self.storage else self, cache)

    def __set_apiURL(self, connection_argument):
        self.api_url = connection_argument.get('endpoint_url')+"/websockets/v3?app_id="+connection_argument.get('app_id')+"&l="+connection_argument.get('lang')+"&brand="+connection_argument.get('brand')

    def __get_apiURL(self):
        return self.api_url

    def get_url(self, original_endpoint):
        if not isinstance(original_endpoint, str):
            raise ConstructionError(f"Endpoint must be a string, passed: {type(original_endpoint)}")

        match = re.match(r'((?:\w*:\/\/)*)(.*)', original_endpoint).groups()
        protocol = match[0] if match[0] == "ws://" else "wss://"
        endpoint = match[1]

        url = protocol+endpoint
        if not is_valid_url(url):
            raise ConstructionError(f'Invalid URL:{original_endpoint}')

        return url

    async def api_connect(self):
        if not self.wsconnection:
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
        self.shouldReconnect = False
        await self.wsconnection.close()
