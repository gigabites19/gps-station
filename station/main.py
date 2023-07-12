import asyncio
import os
from typing import Type

import aiohttp

from logger import logger
from matcher import match_protocol
from protocols import BaseProtocol


class Station:

    def __init__(self, backend_url: str, client_session: aiohttp.ClientSession) -> None:
        self.client_session = client_session
        self.backend_url = backend_url
        self.stream_writers = {}

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client_address, client_port = writer.get_extra_info('peername')
        logger.info(f'Client connected. ({client_address}:{client_port})')

        initial_data = await reader.read(512)
        protocol: Type[BaseProtocol] | None = match_protocol(initial_data)

        if protocol is not None:
            logger.info(f'Identified protocol of newly connected client. ({client_address}:{client_port} - {protocol.__name__}).')
            protocol_instance = protocol(reader, writer, self.client_session, self.backend_url)
            await protocol_instance.loop()
        else:
            logger.warning(f'Could not identify protocol of newly connected client. Closing connection. ({client_address}:{client_port}). data (in bytes): {list(initial_data)}')
            writer.close()
            await writer.wait_closed()

async def main(backend_url: str, station_port: int):
    client_session = aiohttp.ClientSession()
    station = Station(backend_url, client_session)

    server = await asyncio.start_server(station.handle_request, '', station_port)

    address = server.sockets[0].getsockname()
    logger.info(f'Serving on {address}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    backend_url = os.getenv('BACKEND_URL')
    station_port = os.getenv('GPS_STATION_PORT')

    if backend_url is None:
        raise Exception('Backend URL that saves location data is not defined. '
                        'Define "BACKEND_URL" variable in the environment that you are trying to run gps-station in.')

    if station_port is None:
        raise Exception('gps-station\'s port is not defined. '
                        'Define "GPS_STATION_PORT" variable in the environment that you are trying to run gps-station in.')
    else:
        try:
            station_port = int(station_port)
        except ValueError:
            raise ValueError(f'Invalid port number. string "{station_port}" could not be cast to int.')

    asyncio.run(main(backend_url, station_port))

