import re
from exceptions import ProtocolNotRecognized
from protocols.base import BaseProtocol
# TODO: import all of those at once from package
from protocols.h02.h02_location import H02Location # FIXME: weird import
from protocols.h02.h02_command import H02Command
from protocols.h02.h02_command_confirmation import H02CommandConfirmation


protocols = {
    # NOTE: If you change any of the regexes, also check and patch respective protocol's class, also thoroughly inspect backend and make sure nothing breaks.
    r'^\*([A-Z]+),(\d{10}),(V\d),(\d{6}),(A|B|V),(-?\d{4}.\d{4}),(N|S),(-?\d{5}.\d{4}),(E|W),(\d{3}.\d{2}),(\d{3}),(\d{6}),([0-9A-F]+),(\d+),(\d+),(\d+),(\d+)#$': H02Location,
    r'^H02,(\d{10}),(CUT_FUEL|ENABLE_FUEL)$': H02Command,
    r'*': H02CommandConfirmation
}


def match_protocol(raw_data: str) -> BaseProtocol:
    """
    Iterates over the `protocols` dictionary and tries to match each regular expression key to the raw_data.

    :param raw_data: Data sent in by the mobile station
    :returns: Class corresponding to the data. the class later determines what kind of data it is and what to do with it.
    :rtype: BaseProtocol
    :raises ProtocolNotRecognized: if none of the regular expressions match the string.
    """
    for regexp, protocol in protocols.items():
        pattern = re.compile(regexp)
        match = re.match(pattern, raw_data)
        if match:
            return protocol(match, raw_data)
    raise ProtocolNotRecognized(raw_data)
