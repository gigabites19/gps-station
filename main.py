import asyncio
import os
from typing import Type

import aiohttp
from dotenv import load_dotenv

from protocols import BaseProtocol
from matcher import match_protocol

# from exceptions import ProtocolNotRecognized
# from logs import debug_logger, error_logger, critical_logger

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

        # protocol_class: BaseProtocol = identify_protocol(initial_data).expect("protocol could not be identifier. data: ")
        # if protocol_class.keep_alive == True:
        #   device_id = protocol_class.get_device_id()
        #   self.stream_writers['device_id'] = device_id
        #   try:
        #       await protocol_class.loop()
        #   except SocketDisconnected:
        #       if self.stream_writers.get(device_id) is not None:
        #           del self.stream_writers[device_id]
        # else:
        #   * do something once *
















        # while True:
        #     initial_data = await reader.read(128)  # FIXME: this assumes protocol is H02
        #     print(list(initial_data))
        #     try:
        #         initial_data = initial_data.decode()
        #     except UnicodeDecodeError:  # FIXME: this except block exists because some ST-901s send mumbo-jumbo data
        #         """
        #         Some ST-901s send data that can be decoded only on first packet and rest are mumbo-jumbo like the following:
        #         "$0\t\x10`'\x11G8\x15\x06#AC\x182\x06\x04Dv\t\x0e\x00\x03A\xfb\xfd\xfd\xff\x00\x01\x89\xbd\x00\x00\x00\x00\x01\x1a\x14\x03+\x16\x1d5"
        #
        #         `.decode` method fails on this, maybe there is a way to decode this (sinotrackpro.com has no problem parsing this) but I don't have
        #         time to linger on this right now
        #         
        #         We get what we can and then close the connection with the device, thus forcing it to reconnect and send good data again
        #         """
        #         continue
        #
        #     try:
        #         protocol_object = match_protocol(initial_data)
        #
        #         if isinstance(protocol_object, BaseLocation):
        #             # Only save the writer if it's a location connection because that is the TCP stream
        #             # we want to write commands to.
        #             self.stream_writers[protocol_object.payload['device_serial_number']] = writer
        #             
        #             if protocol_object.gprs_blocked:
        #                 # clear out the alarms and make the device catch up if GPRS is blocked
        #                 command = f"*HQ,{protocol_object.payload.get('device_serial_number')},R7,130305#".encode()
        #                 writer.write(command)
        #                 await writer.drain()
        #             else:
        #                 await protocol_object.send_data_uplink(reader, self.session)
        #                 # responding to the device, not sure yet if necessary
        #                 writer.write('*HQ,9172238460,R12,130305#'.encode())
        #                 await writer.drain()
        #         elif isinstance(protocol_object, BaseCommand):
        #             device_writer = self.stream_writers.get(protocol_object.payload.get('device_serial_number'))
        #
        #             if device_writer:
        #                 await protocol_object.send_data_downlink(device_writer, self.session)
        #     except ProtocolNotRecognized:
        #         if initial_data:
        #             error_logger.error(f'Unrecognized protocol {initial_data}')
        #         else:
        #             debug_logger.debug(f'Empty data sent in by a client. Closing connection now.')
        #             writer.close()
        #             await writer.wait_closed()
        #             break
        #     except Exception as e:
        #         critical_logger.critical(f'Uncaught exception: {e}')
        #

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

