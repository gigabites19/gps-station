import re
import asyncio
import aiohttp

class H02CommandConfirmation:

    def __init__(self, regex_match: re.Match, _raw_data: str) -> None:
        super().__init__()
                
        pass

    async def action(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, session: aiohttp.ClientSession):
        print('h02 command confirmation. marking command complete on the server')
    