import re
from dotenv import load_dotenv
from protocols.base import BaseProtocol


class H02(BaseProtocol):
    """
    Class for H02 protocol.

    :param _protocol: Protocol's name, will be sent to the backend server.
    :type _protocol: str
    """

    # TODO: force all subclasses to have some attributes defined

    _protocol: str = "H02"

    """
    after device sends data to the server we must find out which protocol it belongs to. then we must find out what kind of command it is.
    for now it can be one of three: location data, command data (this will be sent from the backend itself) or command confirmation data (which is sent by the device itself)

    here are what we must do for each data point:

    location data: we send the location data to the backend to be saved

    command: we identify who the command is for and then send that command to the mobile station

    command confirmation data: we get the status and send it to the backend to mark the command as complete
    """
