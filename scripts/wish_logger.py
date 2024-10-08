"""
Logger Module
"""

import logging.handlers
from logging.handlers import RotatingFileHandler
from scripts.constant.app_configuration import config


base_path = config['LOG']['basepath']
log_level = config['LOG']['log_level']
file_size = config['LOG']['file_size']
file_count = config['LOG']['file_count']
file_name = config['LOG']['service_name']
LOG_FILE_UPLOADER = f"{base_path}Log/{file_name}"

__logger__ = logging.getLogger("Rotating Log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
__logger__.setLevel(log_level)
handler = RotatingFileHandler(LOG_FILE_UPLOADER + '.log',
                              maxBytes=int(file_size),
                              backupCount=int(file_count))
handler.setFormatter(formatter)
__logger__.addHandler(handler)
__logger__.debug('Logger Initialized')


def get_logger():
    return __logger__
