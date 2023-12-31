from abc import ABC, abstractmethod
import asyncio

import aiohttp

from logger import logger
 
from .packet_decoder import BasePacketDecoder
from .payloads import BaseLocationPayload

class BaseProtocol(ABC):
    """Blueprint for all other protocols to build upon.

    Meant to provide a common interface for concrete implementations of various GPS protocols.
    `BaseProtocol` should never be instantiated directly, instead it defines the interface
    that all protocol implementations should have and establishes some default behavior that
    child classes can use (or override).
 
    Attributes:
        packet_decoder:
            instance of `BasePacketDecoder`'s subclass used to decode data packets sent by device.
        exception_counter:
            Number of exceptions caught during lifetime of the connection - each exception increments this attribute by 1.
        exception_threshold:
            Maximum value `exception_counter` is allowed to reach, connection is closed when threshold value is reached.
        device_imei:
            IMEI of the connected device, not set initially but after protocol is identified and device is in a loop.
        total_sent:
            Total amount of packets sent to the backend in current session.
        stream_writer:
            `asyncio.StreamWriter` instance used to send data to device.
        stream_reader:
            `asyncio.StreamReader` instance used to await and read data sent by devices.
        session:
            Aiohttp session shared by all `BaseProtocol` instances, used to send data uplink.
        backend_url:
            URL of HTTP server that location payloads should be sent to.
    """

    packet_decoder: BasePacketDecoder
    exception_counter: int = 0
    exception_threshold: int = 10
    device_imei: str
    total_sent: int = 0

    def __init__(
        self,
        stream_reader: asyncio.StreamReader,
        stream_writer: asyncio.StreamWriter,
        session: aiohttp.ClientSession,
        backend_url: str
    ) -> None:
        self.stream_reader = stream_reader
        self.stream_writer = stream_writer
        self.client_session = session
        self.backend_url = backend_url

    @classmethod
    @abstractmethod
    def bytes_is_self(cls, raw_bytes: bytes) -> bool:
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

    async def terminate_connection(self) -> None:
        self.stream_writer.close()
        await self.stream_writer.wait_closed()

    async def send_uplink(self, location_payload: BaseLocationPayload) -> None:
        """Sent location data to backend.
        
        Args:
            location_payload:
                A `BaseLocationPayload` subclass' instance containing all formatted location data that is stored in database.
        """
        response = await self.client_session.post(self.backend_url, data=location_payload.__dict__)

        if response.status != 201:
            logger.critical(f'Backend returned unexpected status code. Could not save payload. Status code: {response.status}. Payload: {location_payload}')

