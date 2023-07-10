import asyncio
import os
from typing import Type

import aiohttp
from dotenv import load_dotenv

from logger import logger
from matcher import match_protocol
from protocols import BaseProtocol

load_dotenv()


class Station:

    def __init__(self, backend_address: str, client_session: aiohttp.ClientSession) -> None:
        self.client_session = client_session
        self.backend_address = backend_address
        self.stream_writers = {}

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client_address, client_port = writer.get_extra_info('peername')
        logger.info(f'Client connected. ({client_address}:{client_port})')

        initial_data = await reader.read(512)
        protocol: Type[BaseProtocol] | None = match_protocol(initial_data)

        if protocol is not None:
            logger.info(f'Identified protocol of newly connected client. ({client_address}:{client_port} - {protocol.__name__}).')
            protocol_instance = protocol(reader, writer, self.client_session)
            await protocol_instance.loop()
        else:
            logger.warning(f'Could not identify protocol of newly connected client. Closing connection. ({client_address}:{client_port}). data (in bytes): {list(initial_data)}')
            writer.close()
            await writer.wait_closed()

async def main(backend_address: str):
    client_session = aiohttp.ClientSession()
    station = Station(backend_address, client_session)

    server = await asyncio.start_server(station.handle_request, '', 8090)

    address = server.sockets[0].getsockname()
    logger.info(f'Serving on {address}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    backend_address = os.getenv('BACKEND_URL')

    if backend_address is None:
        raise Exception('Backend address is not defined.'
                        'Define "BACKEND_URL" variable in the environment that you are trying to run Station in.')

    asyncio.run(main(backend_address))

