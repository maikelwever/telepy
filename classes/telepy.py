from TL import TL, deserialize

import io
import socket


class Telepy():

    def __init__(self):
        # Deal with py2 and py3 differences
        try:  # this only works in py2.7
            import configparser
        except ImportError:
            import ConfigParser as configparser
        import mtproto

        self._config = configparser.ConfigParser()
        # Check if credentials is correctly loaded (when it doesn't read anything it returns [])
        if not self._config.read('credentials'):
            print("File 'credentials' seems to not exist.")
            exit(-1)
        ip = self._config.get('App data', 'ip_address')
        port = self._config.getint('App data', 'port')

        self._session = mtproto.Session(ip, port)
        self._session.create_auth_key()

        self._salt = future_salts = self._session.method_call('get_future_salts', num=3)

        self.api_tl = TL('TL_telegram_api.JSON')

    def call_api_method(self, method, **kwargs):
        method_parameters = kwargs.copy()

        if 'api_id' not in method_parameters:
            method_parameters['api_id'] = self._config.getint('App data', 'api_id')

        if 'api_hash' not in method_parameters:
            method_parameters['api_hash'] = self._config.get('App data', 'api_hash')

        for i in range(1, self._session.MAX_RETRY):
            try:
                self._session.send_message(self.api_tl.serialize_method(method, **method_parameters))
                server_answer = self._session.recv_message()
            except socket.timeout:
                print("Retry API call method")
                continue

            try:
                print(deserialize(io.BytesIO(server_answer)))
            except Exception as e:
                print(e)

            try:
                print(self.api_tl.deserialize(io.BytesIO(server_answer)))
            except Exception as e:
                print(e)

            return
