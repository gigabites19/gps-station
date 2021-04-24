import os
import socketserver
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from matcher import match_protocol
from exceptions import ProtocolNotRecognized

# FIXME: DEBUG level logs from requests logger getting logged anyways, probably because it gets reset on line 12

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(filename='exceptions.log', level=logging.DEBUG)
load_dotenv()

socketserver.ThreadingTCPServer.allow_reuse_address = True


class CustomThreadingTCPServer(socketserver.ThreadingTCPServer):

    BACKEND_ADDRESS = os.getenv('BACKEND_URL')


class TCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            self.initial_data = self.request.recv(1024).decode()
            self.protocol_object = match_protocol(self.initial_data)
            print(self.protocol_object.payload)
            self.post_data(data=self.protocol_object.payload)
        except ProtocolNotRecognized:
            if len(self.initial_data) == 0:
                logging.debug(f'Empty data sent in by a client. {self.client_address} | {datetime.now().strftime("%Y, %B %d %H:%M:%S")}')
            else:
                logging.warning(f'Unrecognized protocol: {self.initial_data} | {datetime.now().strftime("%Y, %B %d %H:%M:%S")}')
        except Exception as e:
            logging.critical(f'Uncaught exception: {e} | {datetime.now().strftime("%Y, %B %d %H:%M:%S")}')

    def post_data(self, data: dict) -> None:
        r = requests.post(self.server.BACKEND_ADDRESS, data=data)
        print(r.text)


if __name__ == "__main__":
    server_address = ('', 8090)

    with CustomThreadingTCPServer(server_address, TCPHandler) as server:
        server.serve_forever()
