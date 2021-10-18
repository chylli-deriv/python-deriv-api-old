import asyncio
import json
import logging
import re
from asyncio import Future
from typing import Dict, Optional, Union

import websockets
from rx import operators as op
from rx.subject import Subject
from websockets.legacy.client import WebSocketClientProtocol

from deriv_api.cache import Cache
from deriv_api.custom_future import CustomFuture
from deriv_api.deriv_api_calls import DerivAPICalls
from deriv_api.errors import APIError, ConstructionError, ResponseError
from deriv_api.in_memory import InMemory
from deriv_api.subscription_manager import SubscriptionManager
from deriv_api.utils import dict_to_cache_key, is_valid_url

# TODO TODO subscribe is not calling deriv_api_calls. that's , args not verified. can we improve it ?
# TODO list these features missed
# middleware is missed
# events is missed

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.ERROR
    #level=logging.DEBUG
)


class DerivAPI(DerivAPICalls):
    """
    The minimum functionality provided by DerivAPI, provides direct calls to the API.
    `api.cache` is available if you want to use the cached data

    example
    apiFromEndpoint = deriv_api.DerivAPI({ endpoint: 'ws.binaryws.com', app_id: 1234 });

    param {Object}     options
    param {WebSocketClientProtocol}  options.connection - A ready to use connection
    param {String}     options.endpoint   - API server to connect to
    param {Number}     options.app_id     - Application ID of the API user
    param {String}     options.lang       - Language of the API communication
    param {String}     options.brand      - Brand name
    param {Object}     options.middleware - A middleware to call on certain API actions

    property {Cache} cache - Temporary cache default to {InMemory}
    property {Cache} storage - If specified, uses a more persistent cache (local storage, etc.)
    """
    storage:  None

    def __init__(self, **options: str) -> None:
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

        self.storage: Union[InMemory, Cache, None] = None
        if storage:
            self.storage = Cache(self, storage)

        self.req_id = 0
        self.pending_requests: Dict[str, Subject] = {}
        self.connected = CustomFuture()
        self.subscription_manager: SubscriptionManager = SubscriptionManager(self)
        self.sanity_errors: Subject = Subject()
        self.subscription_manager = SubscriptionManager(self)
        self.wait_data_flag = False
        self.expect_response_types = {}
        self.wait_data_task = CustomFuture().set_result(1)
        # If we have the storage look that one up
        self.cache = Cache(self.storage if self.storage else self, cache)

        self.create_and_watch_task = asyncio.create_task(self.__connect_and_start_watching_data())
        # all created tasks that should be cleared at the end
        self.tasks = []

    async def __connect_and_start_watching_data(self):
        await self.api_connect()
        self.wait_data_flag = True
        self.wait_data_task = asyncio.create_task(self.__wait_data())
        return

    async def __wait_data(self):
        while self.connected.is_resolved() and self.connected.result() and self.wait_data_flag:
            # TODO if there is exception here, then no handle, should try it
            print("calling recv in wait_data wait_data wait_data")
            data = await self.wsconnection.recv()
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(data)
            response = json.loads(data)
            # TODO add self.events stream

            # TODO onopen onclose, can be set by await connection
            req_id = response.get('req_id', None)
            if not req_id or req_id not in self.pending_requests:
                # TODO how is this sanity_errors used
                self.sanity_errors.on_next(APIError("Extra response"))
                print(f"here 118 {req_id}")
                continue
            print("here line 120")
            expect_response: Future = self.expect_response_types.get(response['msg_type'])
            if expect_response and not expect_response.done():
                expect_response.set_result(response)
            request = response['echo_req']

            print("here line 126")
            # When one of the child subscriptions of `proposal_open_contract` has an error in the response,
            # it should be handled in the callback of consumer instead. Calling `error()` with parent subscription
            # will mark the parent subscription as complete and all child subscriptions will be forgotten.

            is_parent_subscription = request and request.get('proposal_open_contract') and not request.get(
                'contract_id')
            if response.get('error') and not is_parent_subscription:
                self.pending_requests[req_id].on_error(ResponseError(response))
                continue

            print("here line 137")
            # on_error will stop a subject object
            if self.pending_requests[req_id].is_stopped and response.get('subscription'):
                # Source is already marked as completed. In this case we should
                # send a forget request with the subscription id and ignore the response received.
                subs_id = response['subscription']['id']
                print("forget again!!!!!!!!!!!!!!!!!!!!!1")
                self.add_task(self.forget(subs_id))
                print("await forget task created")
                continue

            print(f"wait data call on_next response req_id {req_id}")
            print(f"souce id is {self.pending_requests[req_id]}")
            self.pending_requests[req_id].on_next(response)

    def __set_apiURL(self, connection_argument: dict) -> None:
        self.api_url = connection_argument.get('endpoint_url') + "/websockets/v3?app_id=" + connection_argument.get(
            'app_id') + "&l=" + connection_argument.get('lang') + "&brand=" + connection_argument.get('brand')

    def __get_apiURL(self) -> str:
        return self.api_url

    def get_url(self, original_endpoint: str) -> Union[str, ConstructionError]:
        if not isinstance(original_endpoint, str):
            raise ConstructionError(f"Endpoint must be a string, passed: {type(original_endpoint)}")

        match = re.match(r'((?:\w*:\/\/)*)(.*)', original_endpoint).groups()
        protocol = match[0] if match[0] == "ws://" else "wss://"
        endpoint = match[1]

        url = protocol + endpoint
        if not is_valid_url(url):
            raise ConstructionError(f'Invalid URL:{original_endpoint}')

        return url

    async def api_connect(self) -> websockets.WebSocketClientProtocol:
        if not self.wsconnection and self.shouldReconnect:
            self.wsconnection = await websockets.connect(self.api_url)
        # TODO check: don't replace old self.connected, because it will affect the `then` clause
        self.connected.set_result(True)
        return self.wsconnection

    async def send(self, request: dict) -> dict:
        response_future: CustomFuture = CustomFuture.wrap(
            self.send_and_get_source(request).pipe(op.first(), op.to_future()))
        print("creating response_future")
        def set_cache(response):
            self.cache.set(request, response)
            if self.storage:
                self.storage.set(request, response)
            return CustomFuture().set_result(True)
        # TODO  set cache
        #response_future.then(set_cache)
        print("await response future")
        result = await response_future
        print("awaited response future")
        return result

    async def subscribe(self, request):
        return await self.subscription_manager.subscribe(request)

    # TODO fix this one
    # def is_connection_closed(self):
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
        print(f">>>>>>>>>>>>>>>>>>>>>>>\n {request}")
        self.pending_requests[request['req_id']] = pending

        def connected_cb(result):
            return CustomFuture.wrap(asyncio.create_task(self.wsconnection.send(json.dumps(request))))

        def error_cb(exception):
            pending.on_error(exception)
            return CustomFuture().set_result(1)

        self.connected.then(connected_cb).catch(error_cb)
        return pending

    async def subscribe(self, request):
        return await self.subscription_manager.subscribe(request)

    async def forget(self, subs_id):
        print("api forget")
        return await self.subscription_manager.forget(subs_id)

    async def forget_all(self, *types):
        return await self.subscription_manager.forget_all(*types);

    async def disconnect(self) -> None:
        self.shouldReconnect = False
        self.connected = CustomFuture().resolve(False)
        await self.wsconnection.close()

    # TODO remove customfuture, only use async and await ?
    # Or, don't export custom future in the public interfaces ?
    def expect_response(self, *msg_types):
        for msg_type in msg_types:
            if msg_type not in self.expect_response_types:
                def then_cb(val):
                    if not val and self.storage:
                        return CustomFuture().set_result(self.storage.get_by_msg_type(msg_type))
                    return CustomFuture().set_result(val)

                self.expect_response_types[msg_type] = transform_none_to_future(
                    CustomFuture.wrap(asyncio.create_task(self.cache.get_by_msg_type(msg_type))).then(then_cb)
                )

        # expect on a single response returns a single response, not a list
        if len(msg_types) == 1:
            return self.expect_response_types[msg_types[0]]

        return asyncio.gather(map(lambda t: self.expect_response_types[t], msg_types))

    def delete_from_expect_response(self, request):
        response_type = None
        for k in self.expect_response_types.keys():
            if k in request:
                response_type = k
                break

        if response_type and self.expect_response_types[response_type] \
                and self.expect_response_types[response_type].done():
            del self.expect_response_types[response_type]

    # add the backend tasks that are not awaited by others
    # will be awaited in the clear
    def add_task(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.tasks.append(task)
        return task
    # TODO optimize create_and_watch_task and wait_data_task
    # TODO rewrite by `async with`
    # TODO cancel ok, so wait_data_flag is not used ?
    async def clear(self):
        await self.create_and_watch_task
        self.wait_data_flag = False
        self.wait_data_task.cancel()
        for task in self.tasks:
            if(task.done()):
                await task
            else:
                task.cancel('deriv api ended')
        self.tasks = []


def transform_none_to_future(future):
    def then_cb(result):
        new_future = CustomFuture()
        if result is None:
            return CustomFuture()
        return new_future.set_result(result)

    return CustomFuture.wrap(future).then(then_cb)
