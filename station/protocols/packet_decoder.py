from abc import ABC, abstractmethod

from .payloads import BaseLocationPayload


class BasePacketDecoder(ABC):
    """Abstract base class for protocol packet decoders.

    All decoders of various GPS protocols should inherit from this class.
    """

    @abstractmethod
    def decode(self, raw_bytes: bytes) -> BaseLocationPayload:
        """Decode raw bytes sent by a device into a storeable dataclass.

        Args:
            raw_bytes:
                Raw bytes sent by a device.

        Returns:
            Instance of `BaseLocationPayload` subclass.
        """
        pass

