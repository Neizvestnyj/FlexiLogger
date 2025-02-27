import copy
import logging
import os
import sys
from typing import Union

from . import LOG_FILE

os.environ['LOGGER_TIME_INFO'] = 'true'

_LOG_LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')


def get_log_level(env_var: str, default: int) -> int:
    """
    Get logging level from environment variable or use default value.

    :param env_var: environment variable containing log level
    :param default: default log level if environment variable is not set or invalid
    :return: logging level as integer
    """

    level_name = os.getenv(env_var, '').upper()

    return getattr(logging, level_name, default)


class Logger(logging.Logger):
    """
    Customized Logger class for logging to console and optionally to file.
    """

    FORMAT = (
        "\x1b[34m[\x1b[0m%(levelname)s\x1b[34m]:\x1b[0m %(message)s\x1b[34m in file \x1b[0m%(name)s\x1b[34m: %(lineno)d\x1b[0m"
    )

    LOG_FILE_FORMAT = "[%(levelname)s]: %(message)s in %(filename)s:%(lineno)d"

    DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

    def __init__(self,
                 name: str,
                 log_file_path: Union[str, None] = LOG_FILE,
                 console_log_level: int = logging.DEBUG,
                 file_log_level: int = logging.DEBUG,
                 log_file_open_format="a",
                 is_format: bool = True,
                 time_info: bool = True,
                 encoding: str = 'utf-8',
                 ):
        """
        :param name: The name of the logger. Typically, this is the module name or a descriptive name for the logger.
        :param log_file_path: The path to the log file where logs will be written. If None, no file logging will be performed.
        :param console_log_level: The logging level for the console handler. This determines the severity of messages that will be output to the console. Default is logging.DEBUG, which logs all messages.
        :param file_log_level: The logging level for the file handler. This determines the severity of messages that will be written to the log file. Default is logging.DEBUG.
        :param log_file_open_format: The mode in which to open the log file, such as 'a' for append or 'w' for write. Default is 'a' to append to the existing log file.
        :param is_format: Whether to apply formatting to the log messages. If True, log messages will include additional information like log levels and timestamps. Default is True.
        :param time_info: Whether to include timestamps in the log messages. If True, each log message will have a timestamp. Default is True.
        :param encoding: The encoding to use when writing to the log file. Default is 'utf-8'.

        Log levels: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET`
        If the `log_file_path` parameter is provided, the logs will be visible in the log file.
        If `is_format = True` as default, log will be formatted and colorized.
        """
        if log_file_path and log_file_path.lower() == 'false':
            log_file_path = None

        self._log_file_path = log_file_path
        super().__init__(name)

        self.encoding = encoding

        # Enable time formatting if required
        if time_info and os.getenv('LOGGER_TIME_INFO', 'true') in ['true', '1']:
            self.FORMAT = '%(asctime)s.%(msecs)03d: ' + self.FORMAT
            self.LOG_FILE_FORMAT = '%(asctime)s.%(msecs)03d: ' + self.LOG_FILE_FORMAT

        # Read log levels from environment variables
        console_log_level = get_log_level('LOGGER_CONSOLE_LOG_LEVEL', console_log_level)
        file_log_level = get_log_level('LOGGER_FILE_LOG_LEVEL', file_log_level)

        # Add file handler
        if self._log_file_path:
            self._setup_file_handler(log_file_open_format, file_log_level)

        # Add console handler
        if is_format:
            self._setup_console_handler(console_log_level)

    def _setup_file_handler(self, log_file_open_format: str, file_log_level: int) -> None:
        """
        Set up the file handler for logging.

        :param log_file_open_format: mode for opening the log file (e.g., 'a', 'w')
        :param file_log_level: logging level for the file handler
        """

        if not os.path.exists(self._log_file_path):
            with open(self._log_file_path, 'w', encoding=self.encoding):
                self.info(f'Log file: {self._log_file_path} - created')

        fh_formatter = logging.Formatter(self.LOG_FILE_FORMAT, self.DATE_FORMAT)
        file_handler = FormatLogLevelSpaces(self._log_file_path, mode=log_file_open_format, encoding=self.encoding)
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(fh_formatter)
        self.addHandler(file_handler)

    def _setup_console_handler(self, console_log_level: int) -> None:
        """
        Set up the console handler for logging.

        :param console_log_level: logging level for the console handler
        """

        console_color_formatter = logging.Formatter(self.FORMAT, self.DATE_FORMAT)
        console = ColoredConsoleHandler(stream=sys.stdout)
        console.setLevel(console_log_level)
        console.setFormatter(console_color_formatter)
        self.addHandler(console)

    def get_log_file_path(self) -> Union[str, None]:
        return self._log_file_path


class FormatLogLevelSpaces(logging.FileHandler):
    """
    Adjust log level alignment for file logs.
    """

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record with aligned log level.

        :param record: log record to be emitted
        """

        record = copy.copy(record)
        max_length = len(max(_LOG_LEVELS, key=len))
        record.levelname = record.levelname.ljust(max_length)

        super().emit(record)


class ColoredConsoleHandler(logging.StreamHandler):
    """
    Custom console handler with colorized log levels.
    """

    def emit(self, record: logging.LogRecord):
        """
        Emit a colorized log record.

        :param record: log record to be emitted
        """

        record = copy.copy(record)
        level_colors = {
            logging.CRITICAL: '\x1b[41m',  # Red background
            logging.ERROR: '\x1b[31m',  # Red
            logging.WARNING: '\x1b[33m',  # Yellow
            logging.INFO: '\x1b[32m',  # Green
            logging.DEBUG: '\x1b[37m',  # White/Gray
        }
        color = level_colors.get(record.levelno, '\x1b[0m')  # Default
        reset_color = '\x1b[0m'

        max_length = len(max(_LOG_LEVELS, key=len))
        record.levelname = f"{color}{record.levelname.ljust(max_length)}{reset_color}"
        record.msg = f"{color}{record.msg}{reset_color}"
        record.name = f"\x1b[35m{record.name}{reset_color}"

        super().emit(record)


if __name__ == '__main__':
    # Example usage
    logger = Logger(__file__, log_file_path='test.log')
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    logger.critical('Critical message')
