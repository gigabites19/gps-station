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
            #  TODO: log this
            print(f'Could not decode initial bytes sent by a connected device(?). {e.__class__.__name__}: {e}')
            return False
        else:
            return True

    async def loop(self):
        client_address, client_port = self.stream_writer.get_extra_info('peername')

        while True:
            initial_data = await self.stream_reader.read(128)

            if initial_data == b'':
                print(f'Client disconnected. ({client_address}:{client_port} - {self.__class__.__name__}).')  # TODO: change to log
                await self.terminate_connection()
                break
                #  TODO: exception should be raised so writer can be deleted by the station

            try:
                payload = self.packet_decoder.decode(initial_data)
            except (RegExMatchError, BadProtocolError, UnicodeDecodeError) as e:
                # TODO: log this exception
                print(f'Could not decode bytes sent by a connected device(?). {e.__class__.__name__}: {e}')
                self.exception_counter += 1
            except Exception:
                self.exception_counter += 1
                # Unexpected exceptions should also increment `exception_counter` but, unlike expected ones, they should also bubble up
                raise
            else:
                await self.send_uplink(payload)

            if self.exception_counter >= self.exception_threshold:
                # TODO: log this
                print(f'Closing connection with client because exception threshold of {self.exception_threshold} was reached. ({client_address}:{client_port} - {self.__class__.__name__})')
                await self.terminate_connection()
                break

    async def send_uplink(self, location_payload: H02Location) -> None:
        # TODO: replace `localhost:8000` with actual backend address defined in the environment
        response = await self.client_session.post('http://localhost:8000/tracker/add-location/', data=location_payload.__dict__)

        if response.status != 201:
            pass
            # TODO: log, because something went wrong. this method's failure is SMS-notification worthy.
        else:
            # FIXME: remove once not debugging
            print(location_payload.__dict__)

