import os
import asyncio
import aiohttp

from dotenv import load_dotenv
from matcher import match_protocol

from exceptions import ProtocolNotRecognized
from logs import debug_logger, error_logger, critical_logger

load_dotenv()

class ClientContext:
    """
    Class that handles requests, uses one session for all mobile devices that connect to this station,
    mainly here just so I don't have to re-create a session and re-load BACKEND_URL environment variable
    each time a client connects.
    """

    def __init__(self):
        self.counter = 0
        self.session = aiohttp.ClientSession()
        self.server_address = os.getenv('BACKEND_URL')
    
    async def send_to_server(self, payload: dict) -> None:
        """
        Sends clean payload ready for server to aqari main server for saving.

        :param payload: Dictionary containing key,value pair of field name and actual value for the server API to save
        :type payload: dict
        :rtype: None
        """
        response = await self.session.post(self.server_address, data=payload)

        if response.status != 201:
            error_logger.error(f'Server returned unexpected response: {response.text}')
    
    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Fires once data is sent in by a mobile station (GPS), identifies protocol or raises an exception,
        fires method to send the data to server in case everything goes well.

        :param reader: Represents a reader object that provides APIs to read data from the IO stream.
        :type reader: asyncio.StreamReader
        :param writer: Represents a writer object that provides APIs to write data to the IO stream.
        :type writer: asyncio.StreamWriter
        :raises ProtocolNotRecognized: On occasions where protocol is not recognized (includes when sometimes client sends empty data)
        :raises Exception: Other unforeseen exceptions
        :rtype: None
        """
        initial_data = await reader.read(1024)

        initial_data = initial_data.decode()

        print(f'Received: {initial_data}')

        try:
            protocol_object = match_protocol(initial_data)
            response = await self.send_to_server(protocol_object.payload)
        except ProtocolNotRecognized:
            if len(initial_data) == 0:
                debug_logger.debug(f'Empty data sent in by a client.')
            else:
                error_logger.error(f'Unrecognized protocol: {initial_data}')
        except Exception as e:
            critical_logger.critical(f'Uncaught exception: {e}')

        writer.write(b'ok')
        await writer.drain()

        writer.close()
        await writer.wait_closed()


async def main():
    ctx = ClientContext()

    server = await asyncio.start_server(
        ctx.handle_request, '', 8090
    )

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
