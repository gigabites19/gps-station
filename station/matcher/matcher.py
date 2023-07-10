import sys
from typing import Type

from logger import logger
from protocols import BaseProtocol, H02Protocol

protocols = [
    H02Protocol
]

def match_protocol(raw_bytes: bytes) -> Type[BaseProtocol] | None:
    """Identifies protocol based on bytes sent on the stream for the first time.

    Args:
        raw_bytes:
            Raw bytes sent by the device (supposedly, might be from somewhere else, in which case it should ideally be rejected).

    Returns:
        `BaseProtocol`'s subclass object.
    """
    for protocol in protocols:
        try:
            bytes_is_protocol = protocol.bytes_is_self(raw_bytes)
        except Exception as e:
            # Every failure of `protocol.bytes_is_self` should get handled in there.
            # If an exception reaches this `except` block it means something unexpected happened and needs to be addressed urengtly.
            logger.critical(f'Got an unexpected exception when identifying protocol. {e.__class__.__name__}: {e}', exc_info=sys.exc_info()) # TODO: this is SMS worthy
        else:
            return protocol if bytes_is_protocol == True else None

