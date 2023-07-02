"""Module for exceptions that can occur when working with various protocols."""


class RegExMatchError(Exception):
    """Regular expression has no match in a piece of data."""
    pass


class BadProtocolError(Exception):
    """Protocol data structured in an unexpected way.

    This error either means that station has incorrect expectations from the protocol, or
    a malicious actor is connecting by sending a valid protocol data packet at first and then sending packets with arbitrary data.
    Or the device itself is misbehaving.
    """
    pass

