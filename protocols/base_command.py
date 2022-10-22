import asyncio
import aiohttp


class BaseCommand:
    """Base command class that all commands should inherit from"""

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

    async def send_data_downlink(self, writer: asyncio.StreamWriter, session: aiohttp.ClientSession):
        """Sends command to the device"""
        writer.write(f'{self.formatted_command}'.encode())
        await writer.drain()
