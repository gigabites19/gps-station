import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from logs import error_logger

load_dotenv()


class BaseLocation:
    """Base location class that all protocol locations must inherit from"""

    API_ENDPOINT: str = os.getenv('BACKEND_URL')
    _protocol: str = "H02"

    @property
    def payload(self) -> dict:
        """
        Returns a dictionary containing all the attributes the server needs to save GPS location data.

        Loops over all the attributes/methods/class attributes and grabs those that starts with _ and guards against
        those that start with __ to avoid getting python's built-in stuff. We remove the leading underscore because
        attribute names that we send from here must exactly match those defined in backend models.

        :returns: Cleaned, formatted data ready to be saved by the backend server.
        :rtype: dict
        """
        payload = {
            attr[1:]:getattr(self, attr) for attr in dir(self)
            if attr.startswith('_') and not attr.startswith('__')
        }

        return payload

    async def send_data_uplink(self, reader: aiohttp.StreamReader, session: aiohttp.ClientSession):
        """Send data to backend server"""
        response = await session.post(f'{self.API_ENDPOINT}/tracker/add-location/', data=self.payload)

        if response.status == 201:
            response = await response.json(content_type=None)

            return response
        else:
            error_logger.error(f'Server returned an unexpected response: {response.text}')
