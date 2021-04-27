import os
import socketserver
import requests
from dotenv import load_dotenv
from matcher import match_protocol
from exceptions import ProtocolNotRecognized
from logs import debug_logger, error_logger, critical_logger


load_dotenv()

socketserver.ThreadingTCPServer.allow_reuse_address = True


class CustomThreadingTCPServer(socketserver.ThreadingTCPServer):

    BACKEND_ADDRESS = os.getenv('BACKEND_URL')


class TCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            self.initial_data = self.request.recv(1024).decode()
            self.protocol_object = match_protocol(self.initial_data)
            self.post_data(data=self.protocol_object.payload)
        except ProtocolNotRecognized:
            if len(self.initial_data) == 0:
                debug_logger.debug(f'Empty data sent in by client {self.client_address}')
            else:
                error_logger.error(f'Unrecognized protocol {self.initial_data}')
        except Exception as e:
            critical_logger.critical(f'Uncaught exception: {e}')

    def post_data(self, data: dict) -> None:
        r = requests.post(self.server.BACKEND_ADDRESS, data=data)

        if r.status_code != 201:
            error_logger.error(f'Server returned unexpected response: {r.text}')


if __name__ == "__main__":
    server_address = ('', 8090)

    with CustomThreadingTCPServer(server_address, TCPHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Keyboard Interrupt, closing the station.')
