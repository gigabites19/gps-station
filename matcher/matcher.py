import re
from exceptions import ProtocolNotRecognized
from protocols.base import BaseProtocol
from protocols.h02.h02 import H02


protocols = {
    # NOTE: If you change any of the regexes, also check and patch respective protocol's class, also thoroughly inspect backend and make sure nothing breaks.
    **H02.regular_expressions
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
