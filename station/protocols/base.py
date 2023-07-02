from abc import ABC, abstractmethod
import asyncio
 
from .packet_decoder import BasePacketDecoder

class BaseProtocol(ABC):
    """Blueprint for all other protocols to build upon.

    Meant to provide a common interface for concrete implementations of various GPS protocols.
    `packet_decoder` must be defined as a property because it is a mandatory
    attribute for `BaseProtocol` subclass' initialization and python does not provide a way to forbid
    class initialization if it does not implement certain attributes, but it does provide a way
    to do that for methods using `abstractmethod` decorator.
 
    Attributes:
        stream_writer:
            `asyncio.StreamWriter` instance used to send data to device.
        stream_reader:
            `asyncio.StreamReader` instance used to await and read data sent by devices.
        packet_decoder:
            instance of `BasePacketDecoder`'s subclass used to decode data packets sent by device.
    """

    def __init__(self, stream_reader: asyncio.StreamReader, stream_writer: asyncio.StreamWriter) -> None:
        self.stream_reader = stream_reader
        self.stream_writer = stream_writer

    @property
    @abstractmethod
    def packet_decoder(self) -> BasePacketDecoder:
        """Return instance of `BasePacketDecoder`'s subclass."""
        pass

    @staticmethod
    @abstractmethod
    def bytes_is_self(raw_bytes: bytes) -> bool:
        """Determine if bytes belong to calling `BaseProtocol`'s subclass.

        Determine if given list of bytes belong to calling `BaseProtocol`'s subclass.
        Intended usage pseudo code:
        ```python
        bytes = reader.read(100)

        if SomeProtocol::bytes_is_self(bytes):
            SomeProtocol(reader, writer, ...)
        ```

        Args:
            raw_bytes:
                raw bytes sent by a device.

        Returns:
            Either `True` or `False`.
        """
        pass

    @abstractmethod
    async def loop(self) -> None:
        """Continously read, process and deliver data packets sent by a device.

        Read device data, process it and send it to the backend for storage.
        This method should only be called when you are sure that appropriate protocol
        has been correctly identified.
        Each subclass is responsible for closing the connection, keeping connections active
        longer than necessary will use up underlying system's file descriptors.
        """
        pass

