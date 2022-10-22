import os
import asyncio
import aiohttp

from protocols.base_location import BaseLocation
from protocols.base_command import BaseCommand

from dotenv import load_dotenv
from matcher.matcher import match_protocol

from exceptions import ProtocolNotRecognized
from logs import debug_logger, error_logger, critical_logger

load_dotenv()


class Station:

    def __init__(self, session: aiohttp.ClientSession, server_address: str) -> None:
        self.session = session
        self.server_address = server_address
        self.stream_writers = {}

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:

        while True:
            initial_data = await reader.read(1024)
            initial_data = initial_data.decode()

            try:
                protocol_object = match_protocol(initial_data)

                if isinstance(protocol_object, BaseLocation):
                    # Only save the writer if it's a location connection because that is the TCP stream we want to write commands to.
                    self.stream_writers[protocol_object.payload['device_serial_number']] = writer
                    
                    if protocol_object.gprs_blocked:
                        # clear out the alarms and make the device catch up if GPRS is blocked
                        command = f'*HQ,{protocol_object.payload.get("device_serial_number")},R7,130305#'
                        await writer.write(command.encode())
                    else:
                        await protocol_object.send_data_uplink(reader, self.session)
                        await writer.write(b'*HQ,9172238460,R12,130305#') # responding to the device, not sure yet if necessary
                elif isinstance(protocol_object, BaseCommand):
                    device_writer = self.stream_writers.get(protocol_object.payload.get('device_serial_number'))

                    if device_writer:
                        await protocol_object.send_data_downlink(device_writer, self.session)

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

    address = server.sockets[0].getsockname()
    print(f'Serving on {address}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
