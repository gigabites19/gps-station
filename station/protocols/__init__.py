"""Module containing abstractions for concrete implementations of various GPS device communication protocols."""

from .base import BaseProtocol
from .h02 import H02Protocol

__all__ = ('BaseProtocol', 'H02Protocol', )

