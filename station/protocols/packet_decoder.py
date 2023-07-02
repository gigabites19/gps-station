from abc import ABC, abstractmethod

from .payloads import BaseLocationPayload

class BasePacketDecoder(ABC):

     @abstractmethod
     def decode(self, raw_bytes: bytes) -> BaseLocationPayload:
         pass

