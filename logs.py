# https://docs.python.org/3/howto/logging.html
import logging


formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s] - %(message)s')

debug_handler = logging.FileHandler('logs/debug.log')
error_handler = logging.FileHandler('logs/error.log')
critical_handler = logging.FileHandler('logs/critical.log')

for handler in [debug_handler, error_handler, critical_handler]:
    handler.setFormatter(formatter)

debug_logger = logging.getLogger('debug_logger')
error_logger = logging.getLogger('error_logger')
critical_logger = logging.getLogger('critical_logger')

debug_logger.setLevel(logging.DEBUG)

debug_logger.addHandler(debug_handler)
error_logger.addHandler(error_handler)
critical_logger.addHandler(critical_handler)
