import logging
from typing import Literal, Callable
 
# NOTE: Pyright complains when `Literal[..]` is passed `logging.DEBUG` etc. so we use literal numbers instead.
def get_filter_for_handler(handler_level: Literal[20, 30, 40, 50]) -> Callable[[logging.LogRecord], bool]:
    """Return a filter function for logging handler.
    
    Return a logging handler's filter function that filters only
    those log records that have exactly same level as specified in `handler_level` argument.
    This helps to log records only in appropriate files e.g. `logger.critical(..)`
    should only get written in `critical.log` life.

    Args:
        handler_level:
            Level of the `logging.Handler` subclass using the filter
            returned by this function.

    Returns:
        A filter object that accepts logging record as first and only parameter.
        https://docs.python.org/3/library/logging.html#logging.Handler.filter
    """
    def filter_func(record: logging.LogRecord):
        return record.levelno == handler_level

    return filter_func

config = {
    'version': 1,

    'formatters': {
        'basic_formatter': {
            'format': '%(asctime)s - %(message)s'
        }
    },
    
    'handlers': {
        'info_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/info.log',
            'formatter': 'basic_formatter',
            'filters': [ get_filter_for_handler(20) ]
        },

        'warning_handler': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/warning.log',
            'formatter': 'basic_formatter',
            'filters': [ get_filter_for_handler(30) ]
        },

        'error_handler': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/error.log',
            'formatter': 'basic_formatter',
            'filters': [ get_filter_for_handler(40) ]
        },

        'critical_handler': {
            'level': 'CRITICAL',
            'class': 'logging.FileHandler',
            'filename': 'logs/critical.log',
            'formatter': 'basic_formatter',
            'filters': [ get_filter_for_handler(50) ]
        }
    },

    'loggers': {
        'logger': {
            'level': 'INFO',
            'handlers': [ 'info_handler', 'warning_handler', 'error_handler', 'critical_handler' ]
        }
    },
}

