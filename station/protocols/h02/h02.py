from logger import logger
from protocols import BaseProtocol
from protocols.exceptions import RegExMatchError, BadProtocolError

from .packet_decoder import H02PacketDecoder
from .payloads import H02Location

class H02Protocol(BaseProtocol):
    """Implementation of H02 protocol, used by SinoTrack ST-901 trackers."""

    packet_decoder: H02PacketDecoder = H02PacketDecoder()

    @classmethod
    def bytes_is_self(cls, raw_bytes: bytes) -> bool:
        try:
            cls.packet_decoder.decode(raw_bytes)
        except (RegExMatchError, BadProtocolError, UnicodeDecodeError) as e:
            logger.warning(f'Could not decode initial bytes sent by a connected device(?). {e.__class__.__name__}: {e}')
            return False
        else:
            return True

    async def loop(self):
        client_address, client_port = self.stream_writer.get_extra_info('peername')

        while True:
            # FIXME: TCP is a stream-based protocol, instead of expecting "packets" we should
            # read the first byte, identify which mode device is sending the record with:
            # if first byte is '*' => ASCII mode, if first byte is '$' => binary mode - also called standard mode.
            #
            # After identifying record mode, we should read and add subsequent bytes to a buffer.
            # We can know that record is complete in different ways for each mode.
            # We can know that ASCII mode record is complete when '#' byte is sent. (All ASCII mode records end with #).
            # Binary/standard mode records always have fixed length of 45 bytes including '$'.
            initial_data = await self.stream_reader.read(128)

            if initial_data == b'':
                logger.info(f'Client closed connection. ({client_address}:{client_port} - {self.__class__.__name__}).')
                await self.terminate_connection()
                break
                #  TODO: exception should be raised so writer can be deleted by the station

            try:
                payload = self.packet_decoder.decode(initial_data)
            except (RegExMatchError, BadProtocolError, UnicodeDecodeError) as e:
                logger.warning(f'Could not decode bytes sent by a connected device(?). {e.__class__.__name__}: {e}')
                self.exception_counter += 1
            # Unexpected exceptions should also increment `exception_counter` but, unlike expected ones, they should also bubble up
            except Exception:
                self.exception_counter += 1
                raise
            else:
                await self.send_uplink(payload)

                # Purpose of this is not documented anywhere but sinotrackpro.com platform itself
                # replies with such command if you connect to it ('45.112.204.245', 8090) with TCP socket.
                self.stream_writer.write(f'*HQ,{self.device_imei},R12,{payload.time}#'.encode())
                await self.stream_writer.drain()

                self.total_sent += 1
                self.device_imei = payload.device_serial_number
                logger.info(f'Processed and sent data sent by IMEI:{payload.device_serial_number} to backend. Total sent: {self.total_sent}')

            if self.exception_counter >= self.exception_threshold:
                logger.warning(f'Closing connection with client because exception threshold of {self.exception_threshold} was reached. ({client_address}:{client_port} - {self.__class__.__name__})')
                await self.terminate_connection()
                break

