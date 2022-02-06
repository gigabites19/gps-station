import re
from exceptions import ProtocolNotRecognized
from protocols.base import BaseProtocol
# TODO: import all of those at once from package
from protocols.h02.h02_location import H02Location # FIXME: weird import
from protocols.h02.h02_command import H02Command


protocols = {
    # NOTE: If you change any of the regexes, also check and patch respective protocol's class, also thoroughly inspect backend and make sure nothing breaks.
    H02Location.LOCATION_REGEX: H02Location,
    r'^H02,(\d{10}),(CUT_FUEL|ENABLE_FUEL)$': H02Command,
    H02Location.COMMAND_CONFIRMATION_REGEX: H02Location
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
