import re
from exceptions import ProtocolNotRecognized
from protocols.base import BaseProtocol
from protocols.h02 import H02

protocols = {
    # NOTE: If you change any of the regexes, also check and patch respective protocol's class, also thoroughly inspect backend and make sure nothing breaks.
    '^\*([A-Z]+),(\d{10}),(V\d),(\d{6}),(A|B|V),(-?\d{4}.\d{4}),(N|S),(-?\d{5}.\d{4}),(E|W),(\d{1,3}.\d{2}),(\d{1,3}),(\d{6}),([0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+)#$': H02,
}


def match_protocol(string: str) -> BaseProtocol:
    """
    Iterates over the `protocols` dictionary and tries to match each regular expression key to the string.

    :param string: Data sent in by the mobile station
    :returns: Class corresponding to the data, initialized re.Match object.
    :rtype: BaseProtocol
    :raises ProtocolNotRecognized: if none of the regular expressions match the string.
    """
    for regexp, protocol in protocols.items():
        pattern = re.compile(regexp)
        match = re.match(pattern, string)
        if match:
            return protocol(match, string)
    raise ProtocolNotRecognized(string)
