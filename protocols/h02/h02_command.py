import re
from datetime import datetime
import asyncio
import aiohttp
from protocols.h02.h02 import H02

class H02Command(H02):

    COMMANDS = {
        r'H02,(\d{10}),CUT_FUEL': lambda device_serial_number, time: '*HQ,%s,S20,%s,1,1#' % (device_serial_number, time),
        r'H02,(\d{10}),ENABLE_FUEL': lambda device_serial_number, time: '*HQ,%s,S20,%s,1,0#' % (device_serial_number, time)
    }

    def __init__(self, regex_match: re.Match, _raw_data: str) -> None:
        super().__init__()

        self._device_serial_number = regex_match.group(1)

        for regexp, formatter in self.COMMANDS.items():
            pattern = re.compile(regexp)
            match = re.match(pattern, _raw_data)

            if match:
                self.formatted_command = formatter(self._device_serial_number, datetime.now().strftime('%H%M%S'))
    
    async def action(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, session: aiohttp.ClientSession):
        print(self.formatted_command)
        await writer.write(f'{self.formatted_command}'.encode())
