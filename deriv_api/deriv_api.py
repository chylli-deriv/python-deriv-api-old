#
import websocket
import json
#from websocket._exceptions import WebSocketConnectionClosedException

class deriv_api:
    wsconnection = ''

    def __init__(self, app_id, endpoint = 'frontend.binaryws.com', lang = 'EN', brand = ''):
        connectionArgument = {
            'app_id': str(app_id),
            'endpoint': endpoint,
            'lang': lang,
            'brand': brand
        }

        self.wsconnection = self.__connect(connectionArgument)
        
        if (self.wsconnection):
            self.wsconnection.run_forever(ping_interval=60, ping_timeout=10, ping_payload={'ping':1})

    def __connect(self, connectionArgument):
        apiUrl = "wss://ws.binaryws.com/websockets/v3?app_id="+connectionArgument['app_id']+"&l="+connectionArgument['lang']+"&brand="+connectionArgument['brand']
        wsconnection = websocket.WebSocketApp(apiUrl, on_message=self.on_message, on_error=self.on_error, on_ping=self.on_ping, on_pong=self.on_pong)
        return wsconnection

    # error may be webSocketTimeoutException, WebSocketConnectionClosedException... 
    def on_error(self, wsconnection, error):
        return 'Something went wrong while connecting API.'

    def on_message(self, wsconnection, message):
        data = json.loads(message)
        
        if 'error' in data.keys():
            return "Error"

        return data

    def on_ping(self, wsconnection, message):
        return message

    def on_pong(self, wsconnection, message):
        data = json.loads(message)

        return data['ping']

    #def set_endpoint(self, endpoint): todo later improvement
    #    self.endpoint = endpoint

    #def get_endpoint(self):
    #    return self.endpoint
