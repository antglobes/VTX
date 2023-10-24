import logging
import sys
from pathlib import Path


from configparser import ConfigParser


def clear_previous_logs():
    path = Path('src').resolve().parent.joinpath('/data/files/output.log').as_posix()
    with open(path, 'w+') as log_file:
        log_file.write('\n')



class LoggingUtilities:

    def __init__(self):
        self.parser = ConfigParser()
        self.logger = None

    def setup_logger(self):
        self.logger = logging.getLogger('System_logger')
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(filename=Path('src').resolve().parent.parent
                                           .joinpath('data/files/output.log').as_posix())
        file_handler.setLevel(logging.DEBUG)
        verbose_format = logging.Formatter('%(asctime)s | [%(levelname)s:%(name)s] | [%(module)s:%(funcName)s:%(lineno)s] | %(message)s')
        file_handler.setFormatter(verbose_format)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.WARNING)
        simple_format = logging.Formatter('%(asctime)s | [%(levelname)s:%(name)s] | %(message)s')
        stream_handler.setFormatter(simple_format)
        self.logger.addHandler(stream_handler)


    def create_log_entry(self, level, message):
        self.logger.log(level=level, msg=message)

    def start_logger(self):
        clear_previous_logs()
        self.setup_logger()
        self.create_log_entry(level=logging.CRITICAL, message='Starting logger')