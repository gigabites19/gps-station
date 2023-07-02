from protocols import BaseProtocol

from .packet_decoder import H02PacketDecoder

class H02Protocol(BaseProtocol):
    """Implementation of H02 protocol, mostly used by ST-901 trackers by SinoTrack."""

    @property
    def packet_decoder(self) -> H02PacketDecoder:
        return H02PacketDecoder()

    @staticmethod
    def bytes_is_self(raw_bytes: bytes) -> bool:
        return raw_bytes.startswith((b'*', b'$'))

    async def loop(self):
        while True:
            initial_data = await self.stream_reader.read(128)

            if initial_data == b'':
                print("Client disconnected: ", self.stream_writer.get_extra_info('peername'))  # TODO: change to log
                self.stream_writer.close()
                await self.stream_writer.wait_closed()
                break
                #  TODO: exception should be raised so writer can be deleted by the station

            # TODO: add try/catch block and error counter, if it exceeds threshold then
            # TODO: stop this loop. if eceptions raised from `packet_decoder.decode` are
            # TODO: hitting this loop often, it means something is wrong and needs attention.
            payload = self.packet_decoder.decode(initial_data)
            print(payload)

