from deriv_api.cache import Cache
from deriv_api.deriv_api_calls import DerivAPICalls
from deriv_api.in_memory import InMemory
from deriv_api.subscription_manager import  SubscriptionManager
import websockets
from websockets.legacy.client import WebSocketClientProtocol
import json
import logging
from deriv_api.errors import APIError, ConstructionError
from deriv_api.utils import dict_to_cache_key, is_valid_url
import re
from rx.subject import Subject
from deriv_api.custom_future import CustomFuture
from typing import Optional, Dict
import asyncio
from rx import operators as op

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
    param {WebSocket}  options.connection - A ready to use connection
    param {String}     options.endpoint   - API server to connect to
    param {Number}     options.app_id     - Application ID of the API user
    param {String}     options.lang       - Language of the API communication
    param {String}     options.brand      - Brand name
    param {Object}     options.middleware - A middleware to call on certain API actions

    property {Cache} cache - Temporary cache default to {InMemory}
    property {Cache} storage - If specified, uses a more persistent cache (local storage, etc.)
    """
    storage = ''
    def __init__(self, **options):
        endpoint = options.get('endpoint', 'frontend.binaryws.com')
        lang = options.get('lang', 'EN')
        brand = options.get('brand', '')
        cache = options.get('cache', InMemory())
        storage = options.get('storage')
        self.wsconnection: Optional[WebSocketClientProtocol] = None

        if options.get('connection'):
            self.wsconnection: Optional[WebSocketClientProtocol] = options.get('connection')
        else:
            if not options.get('app_id'):
                raise ConstructionError('An app_id is required to connect to the API')

            connection_argument = {
                'app_id': str(options.get('app_id')),
                'endpoint_url': self.get_url(endpoint),
                'lang': lang,
                'brand': brand
            }
            self.__set_apiURL(connection_argument)
            self.shouldReconnect = True

        if storage:
            self.storage = Cache(self, storage)

        self.req_id = 0
        self.pending_requests: Dict[str, Subject] = {}
        self.connected = CustomFuture()
        self.subscription_manager: SubscriptionManager = SubscriptionManager(self)
        self.sanity_errors: Subject = Subject()
        self.wait_data_flag = False
        self.wait_data_task = CustomFuture().set_result(1)
        # If we have the storage look that one up
        self.cache = Cache(self.storage if self.storage else self, cache)

        self.create_and_watch_task = asyncio.create_task(self.__connect_and_start_watching_data())

    async def __connect_and_start_watching_data(self):
        await self.api_connect()
        self.wait_data_flag = True
        self.wait_data_task = asyncio.create_task(self.__wait_data())
        return

    async def __wait_data(self):
        while self.connected.is_resolved() and self.connected.result() and self.wait_data_flag:
            data = await self.wsconnection.recv()
            response = json.loads(data)
            # TODO add self.events stream

            req_id = response.get('req_id', None)
            if not req_id or req_id not in self.pending_requests:
                self.sanity_errors.on_next(APIError("Extra response"))
                continue

            # TODO expect_response_types
            request = response['echo_req']
            # TODO process poc stream
            # TODO process subscription
            self.pending_requests[req_id].on_next(response)

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
        if not self.wsconnection and self.shouldReconnect:
            self.wsconnection = await websockets.connect(self.api_url)

        self.connected.set_result(True)
        return self.wsconnection

    async def send(self, request):
        response_future: CustomFuture = CustomFuture.wrap(self.send_and_get_source(request).pipe(op.first(), op.to_future()))
        # TODO cache
        return await response_future


    async def subscribe(self, request):
        return await self.subscription_manager.subscribe(request)

    # TODO fix this one
    #def is_connection_closed(self):
    #    return self.connection.ready_state == 2 or self.connection.ready_state == 3


    # TODO
    # 1 add all funcs taht include subscription_manager
    # 2. check all functs that subscription_manager will called
    # 3. check async on all funcs of 1 and 2
    # 4. some function like "send" or manager `create_new_source` will await the first response
    # 5. make sure that first response can be got by other subscription
    # 6. dict.get(key, value) to set value
    def send_and_get_source(self, request: dict):
        pending = Subject()
        if 'req_id' not in request:
            self.req_id += 1
            request['req_id'] = self.req_id
        self.pending_requests[request['req_id']] = pending
        def connected_cb(result):
            return CustomFuture.wrap(asyncio.create_task(self.wsconnection.send(json.dumps(request))))
        def error_cb(exception):
            pending.on_error(exception)
            return CustomFuture().set_result(1)
        self.connected.then(connected_cb).catch(error_cb)
        return pending

    def parse_response(self, message):
        data = json.loads(message)
        return data

    async def disconnect(self):
        self.shouldReconnect = False
        self.connected = CustomFuture.resolve(False)
        await self.wsconnection.close()

    # TODO optimize create_and_watch_task and wait_data_task
    # TODO rewrite by `async with`
    # TODO cancel ok, so wait_data_flag is not used ?
    async def clear(self):
        print("clearing.....")
        await self.create_and_watch_task
        print("waiting.............")
        self.wait_data_flag = False
        self.wait_data_task.cancel()