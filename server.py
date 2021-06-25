import os
import asyncio
import aiohttp

from dotenv import load_dotenv
from matcher import match_protocol

from exceptions import ProtocolNotRecognized
from logs import debug_logger, error_logger, critical_logger

load_dotenv()


class Station:

    def __init__(self, session: aiohttp.ClientSession, server_address: str) -> None:
        self.session = session
        self.server_address = server_address

    async def send_to_server(self, payload: dict) -> None:
        response = await self.session.post(self.server_address, data=payload)

        if response.status == 201:
            # Here server should any commands that might be there in queue for the
            pass
        else:
            error_logger.error(f'Server returned unexpected response: {response.text}')


    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:

        while True:
            initial_data = await reader.read(1024)
            initial_data = initial_data.decode()

            print(initial_data)

            try:
                protocol_object = match_protocol(initial_data)
                await self.send_to_server(protocol_object.payload)
            except ProtocolNotRecognized:
                if initial_data:
                    error_logger.error(f'Unrecognized protocol {initial_data}')
                else:
                    debug_logger.debug(f'Empty data sent in by a client. Closing connection now.')
                    writer.close()
                    await writer.wait_closed()
                    break
            except Exception as e:
                critical_logger.critical(f'Uncaught exception: {e}')

            

async def main():
    session = aiohttp.ClientSession()
    server_address = os.getenv('BACKEND_URL')

    station = Station(session, server_address)

    server = await asyncio.start_server(station.handle_request, '', 8090)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
