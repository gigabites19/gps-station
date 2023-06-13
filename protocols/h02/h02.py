from protocols.base import BaseProtocol
from .actions.location import Location
from .actions.command import Command
from .actions.custom_command import CustomCommand


class H02(BaseProtocol):
    """
    Class for H02 protocol.

    :param _protocol: Protocol's name, will be sent to the backend server.
    :type _protocol: str
    :param regular_expressions: regular expressions of the protocol that match classes that perform actions linked with this protocol
    :type regular_expressions: dict
    """

    # TODO: force all subclasses to have some attributes defined
    _protocol: str = "H02"

    # TODO: test that all protocols define those with protocol name appended in front for dictionary key
    regular_expressions: dict = {
        r'^\*([A-Z]+),(\d{10}),(V\d),(\d{6}),(A|B|V),(-?\d{4}.\d{4}),(N|S),(-?\d{4,5}.\d{4}),(E|W),(\d{1,3}.\d{2}),(\d{1,3}),(\d{6}),([0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+)(,\d+\D?)?#$': Location,
        r'^\*([A-Z]+),(\d{10}),(V\d),(S\d+),(OK|DONE),(\d{6}),(\d{6}),(A|B|V),(-?\d{4}.\d{4}),(N|S),(-?\d{4,5}.\d{4}),(E|W),(\d{1,3}.\d{2}),(\d{1,3}),(\d{6}),([0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+)(,\d+\D?)?#$': Location,
        r'^H02,(\d{10}),(CUT_FUEL|ENABLE_FUEL)$': Command,
        # For testing
        r'custom\((\d{10})\)\((.*)\)': CustomCommand
    }

