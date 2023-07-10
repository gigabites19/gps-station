"""Package that contains all logging-related configuration of this project."""

import logging
from logging.config import dictConfig

from .config import config

dictConfig(config)

logger = logging.getLogger('logger')

__all__ = ('logger', )

