from protocols.packet_decoder import BasePacketDecoder
from protocols.exceptions import RegExMatchError, BadProtocolError

from protocols.h02.payloads import H02Location

from .decoders import decode_h02_ascii_packet, decode_h02_binary_packet


class H02PacketDecoder(BasePacketDecoder):

    def decode(self, raw_bytes: bytes) -> H02Location:
        """Decode location packet sent by a device using H02 protocol.

        Args:
            raw_bytes:
                Raw bytes of the packets.

        Returns:
            `H02Location` object that contains all required data to be saved in the backend.

        Raises:
            BadProtocolError: If data packet begins unexpectedly (Neither '*' nor '$').
            UnicodeDecodeError: If ASCII mode can not be decoded properly.
            RegExMatchError: If one of the decoders fail to decode a certain parameter (they use regular expressions internally).
        """
        try:
            if raw_bytes.startswith(b'*'):
                return decode_h02_ascii_packet(raw_bytes)
            elif raw_bytes.startswith(b'$'):
                return decode_h02_binary_packet(raw_bytes)
            else:
                raise BadProtocolError(f'Expected H02 packet to start with either "*" or "$" instead got (bytes): {list(raw_bytes)}')
        except (BadProtocolError, UnicodeDecodeError, RegExMatchError):
            raise

