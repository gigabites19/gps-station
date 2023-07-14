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
                self.total_sent += 1
                self.device_imei = payload.device_serial_number
                logger.info(f'Processed and sent data sent by IMEI:{payload.device_serial_number} to backend. Total sent: {self.total_sent}')

            if self.exception_counter >= self.exception_threshold:
                logger.warning(f'Closing connection with client because exception threshold of {self.exception_threshold} was reached. ({client_address}:{client_port} - {self.__class__.__name__})')
                await self.terminate_connection()
                break

