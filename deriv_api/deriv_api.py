#
#import websocket
class deriv_api:
    connection = ''
    lang = 'EN'
    brand = 'binary'

    def __init__(self, app_id, connection, endPoint = 'frontend.binaryws.com', lang = 'EN', brand = '') -> None:
        if connection :
            self.connection = connection
        else:
            self.endPoint = endPoint
            self.lang = lang
            self.brand = brand
            self.__connect()
        pass

    def __connect(self) -> None:
        #apiUrl = "wss://ws.binaryws.com/websockets/v3?app_id="+self.app_id
        #ws = websocket.WebSocketApp(apiUrl, on_message=on_message, on_open=on_open)
        #ws.run_forever()
        pass

    def hello(self) -> str:
        """
        A dummy function
        """

        return "Hello world!"
