"""Module for simple protocol identification"""

from typing import Type
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
        if protocol.bytes_is_self(raw_bytes):
            return protocol

