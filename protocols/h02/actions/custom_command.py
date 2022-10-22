import re
import asyncio
import aiohttp
from datetime import datetime
from protocols.base_command import BaseCommand

class CustomCommand(BaseCommand):

    def __init__(self, regex_match: re.Match, _raw_data: str) -> None:
        self._device_serial_number = regex_match.group(1)
        self.formatted_command = regex_match.group(2)
    
    async def send_data_downlink(self, writer: asyncio.StreamWriter, session: aiohttp.ClientSession):
        writer.write(f'{self.formatted_command}'.encode())
        await writer.drain()
