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


        self.counter = 0

    
    async def mark_command_complete(self, command_id: str) -> None:
        response = await self.session.post(f'{self.server_address}/tracker/mark-command-complete/', data={'id': command_id})
        print(f'marking command {command_id} complete')
        print(response.status)

    async def send_to_server(self, payload: dict) -> None:
        response = await self.session.post(f'{self.server_address}/tracker/add-location/', data=payload)

        if response.status == 201:
            response = await response.json()
            
            return response 
        else:
            error_logger.error(f'Server returned unexpected response: {response.text}')

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:

        while True:
            initial_data = await reader.read(1024)
            initial_data = initial_data.decode()

            print(initial_data)

            try:
                protocol_object = match_protocol(initial_data)
                command = await self.send_to_server(protocol_object.payload)
                if command and not command['fulfilled']:
                    await writer.write(command['command_code'].encode())
                    await self.mark_command_complete(command['id'])
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
