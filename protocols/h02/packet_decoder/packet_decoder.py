from protocols.packet_decoder import BasePacketDecoder

from protocols.h02.payloads import H02Location

from .decoders import decode_h02_ascii_packet, decode_h02_binary_packet


class H02PacketDecoder(BasePacketDecoder):
    def decode(self, raw_bytes: bytes) -> H02Location:
        if raw_bytes.startswith(b'*'):
            return decode_h02_ascii_packet(raw_bytes)
        elif raw_bytes.startswith(b'$'):
            return decode_h02_binary_packet(raw_bytes)
        # TODO: raise an exception

