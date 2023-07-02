import asyncio
import os
from typing import Type

import aiohttp
from dotenv import load_dotenv

from protocols import BaseProtocol
from matcher import match_protocol

load_dotenv()


class Station:

    def __init__(self, session: aiohttp.ClientSession, server_address: str) -> None:
        self.session = session
        self.server_address = server_address
        self.stream_writers = {}

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client_address, client_port = writer.get_extra_info('peername')
        print(f'Client connected. ({client_address}:{client_port})')  # TODO: change to log

        initial_data = await reader.read(512)
        protocol: Type[BaseProtocol] | None = match_protocol(initial_data)

        if protocol is not None:
            print(f'Identified protocol of newly connected client. ({client_address}:{client_port} - {protocol.__name__}).')  # TODO: change to log
            protocol_instance = protocol(reader, writer)
            await protocol_instance.loop()
        else:
            print(f'Could not identify protocol for client. Closing connection. ({client_address}:{client_port}).')  # TODO: change to log. send sms?
            writer.close()
            await writer.wait_closed()

async def main():
    session = aiohttp.ClientSession()
    server_address = os.getenv('BACKEND_URL')

    if server_address is None:
        raise Exception("Server address is not defined.")

    station = Station(session, server_address)

    server = await asyncio.start_server(station.handle_request, '', 8090)

    address = server.sockets[0].getsockname()
    print(f'Serving on {address}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

