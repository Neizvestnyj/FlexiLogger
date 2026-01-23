import copy
import datetime
import json
import logging
import os
import re
import sys
import time
from logging.handlers import RotatingFileHandler
from typing import Any, MutableMapping

_LOG_LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET")

# Standard attributes of LogRecord to exclude from JSON extra fields
_STANDARD_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


def get_log_level(env_var: str, default: int) -> int:
    """
    Get logging level from environment variable or use default value.

    :param env_var: Environment variable name.
    :param default: Default logging level if variable is not set.
    :return: Logging level as integer.
    """
    level_name = os.getenv(env_var, "").upper()
    return getattr(logging, level_name, default)


def _parse_timezone(tz_str: str | None) -> datetime.timezone | None:
    """
    Parse timezone string into datetime.timezone object.

    :param tz_str: Timezone string (e.g., "UTC", "UTC+3", "UTC-05:00", "LOCAL").
    :return: datetime.timezone object or None for local time.
    """
    if not tz_str:
        return datetime.timezone.utc

    tz_str = tz_str.strip().upper()

    if tz_str == "LOCAL":
        return None

    if tz_str == "UTC":
        return datetime.timezone.utc

    match = re.match(r"^UTC([+-])(\d+)(?::(\d+))?$", tz_str)
    if match:
        sign = 1 if match.group(1) == "+" else -1
        hours = int(match.group(2))
        minutes = int(match.group(3)) if match.group(3) else 0
        offset = datetime.timedelta(hours=hours, minutes=minutes)
        return datetime.timezone(sign * offset)

    return datetime.timezone.utc


def _get_time_converter(tz: datetime.timezone | None):
    """
    Create a time converter function for the specified timezone.

    :param tz: datetime.timezone object or None for local time.
    :return: converter function compatible with logging.Formatter.converter.
    """
    if tz is None:
        return time.localtime

    def converter(timestamp: float | None = None) -> time.struct_time:
        if timestamp is None:
            timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp, tz)
        return dt.timetuple()

    return converter


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for structured logging.
    Includes support for extra context fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified record as text (JSON).

        :param record: The log record to format.
        :return: A JSON formatted string.
        """
        log_record: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key not in _STANDARD_RECORD_ATTRS and not key.startswith("_"):
                log_record[key] = value

        return json.dumps(log_record)


class FormatLogLevelSpaces(RotatingFileHandler):
    """
    Adjust log level alignment for file logs with rotation support.
    """

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record.

        :param record: The log record to emit.
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

        :param record: The log record to emit.
        """
        record = copy.copy(record)
        level_colors = {
            logging.CRITICAL: "\x1b[41m",  # Red background
            logging.ERROR: "\x1b[31m",  # Red
            logging.WARNING: "\x1b[33m",  # Yellow
            logging.INFO: "\x1b[32m",  # Green
            logging.DEBUG: "\x1b[37m",  # White/Gray
        }
        color = level_colors.get(record.levelno, "\x1b[0m")
        reset_color = "\x1b[0m"

        max_length = len(max(_LOG_LEVELS, key=len))
        record.levelname = f"{color}{record.levelname.ljust(max_length)}{reset_color}"
        record.msg = f"{color}{record.msg}{reset_color}"
        record.name = f"\x1b[35m{record.name}{reset_color}"

        super().emit(record)


class FlexiLoggerAdapter(logging.LoggerAdapter):
    """
    Adapter to handle context binding.
    """

    def __init__(self, logger: logging.Logger, extra: dict[str, Any] | None = None):
        """
        Initialize the adapter with a logger and extra context.

        :param logger: The logger to adapt.
        :param extra: Dictionary of extra context to bind.
        """
        super().__init__(logger, extra or {})

    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> tuple[Any, MutableMapping[str, Any]]:
        """
        Process the log message and keyword arguments.
        Merges the bound context into the 'extra' keyword argument.

        :param msg: The log message.
        :param kwargs: Keyword arguments for the log call.
        :return: Tuple of (message, kwargs).
        """
        # Ensure self.extra is treated as a dict for pyright
        context: dict[str, Any] = self.extra if isinstance(self.extra, dict) else {}
        extra = context.copy()

        if "extra" in kwargs and isinstance(kwargs["extra"], dict):
            extra.update(kwargs["extra"])

        kwargs["extra"] = extra
        return msg, kwargs

    def bind(self, **kwargs: Any) -> "FlexiLoggerAdapter":
        """
        Return a new adapter with the merged context.

        :param kwargs: Key-value pairs to add to the context.
        :return: A new FlexiLoggerAdapter instance.
        """
        context: dict[str, Any] = self.extra if isinstance(self.extra, dict) else {}
        new_extra = context.copy()
        new_extra.update(kwargs)
        return FlexiLoggerAdapter(self.logger, new_extra)


class Logger(logging.Logger):
    """
    Customized Logger class for logging to console and optionally to file.
    """

    FORMAT = "\x1b[34m[\x1b[0m%(levelname)s\x1b[34m]:\x1b[0m %(message)s\x1b[34m in file \x1b[0m%(name)s\x1b[34m: %(lineno)d\x1b[0m"
    LOG_FILE_FORMAT = "[%(levelname)s]: %(message)s in %(filename)s:%(lineno)d"
    DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

    def __init__(
        self,
        name: str,
        log_file_path: str | None = None,
        console_log_level: int = logging.DEBUG,
        file_log_level: int = logging.DEBUG,
        log_file_open_format: str = "a",
        is_format: bool = True,
        time_info: bool = True,
        encoding: str = "utf-8",
        timezone: str | None = None,
        date_format: str | None = None,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        json_format: bool | None = None,
    ):
        """
        Initialize the custom logger.

        :param name: The name of the logger.
        :param log_file_path: The path to the log file.
        :param console_log_level: The logging level for the console handler.
        :param file_log_level: The logging level for the file handler.
        :param log_file_open_format: The mode in which to open the log file.
        :param is_format: Whether to apply formatting to the log messages.
        :param time_info: Whether to include timestamps in the log messages.
        :param encoding: The encoding to use when writing to the log file.
        :param timezone: Timezone for timestamps.
        :param date_format: The format string for timestamps.
        :param max_bytes: Maximum size of log file in bytes before rotation.
        :param backup_count: Number of backup log files to keep.
        :param json_format: Whether to log in JSON format. Defaults to LOGGER_JSON_FORMAT env var.
        """
        if not log_file_path:
            log_file_path = os.getenv("LOG_PATH")

        if log_file_path and log_file_path.lower() == "false":
            log_file_path = None

        self._log_file_path = log_file_path
        super().__init__(name)

        self._encoding = encoding

        if timezone is None:
            timezone = os.getenv("LOGGER_TIMEZONE")

        self._tz_object = _parse_timezone(timezone)
        self._time_converter = _get_time_converter(self._tz_object)

        if json_format is None:
            json_format = os.getenv("LOGGER_JSON_FORMAT", "false").lower() in ("true", "1")
        self._json_format = json_format

        env_time_info = os.getenv("LOGGER_TIME_INFO", "true")
        if time_info and env_time_info in ["true", "1"]:
            self.FORMAT = "%(asctime)s.%(msecs)03d: " + self.FORMAT
            self.LOG_FILE_FORMAT = "%(asctime)s.%(msecs)03d: " + self.LOG_FILE_FORMAT

        console_log_level = get_log_level("LOGGER_CONSOLE_LOG_LEVEL", console_log_level)
        file_log_level = get_log_level("LOGGER_FILE_LOG_LEVEL", file_log_level)

        if self._log_file_path:
            self._setup_file_handler(
                self._log_file_path,
                log_file_open_format,
                file_log_level,
                date_format,
                max_bytes,
                backup_count,
            )

        if is_format:
            self._setup_console_handler(console_log_level, date_format)

    def bind(self, **kwargs: Any) -> FlexiLoggerAdapter:
        """
        Create a new LoggerAdapter with bound context.

        Example:
            log = logger.bind(user_id=123)
            log.info("Action") # JSON will include "user_id": 123

        :param kwargs: Context to bind.
        :return: A FlexiLoggerAdapter instance.
        """
        return FlexiLoggerAdapter(self, kwargs)

    def _setup_file_handler(
        self,
        log_path: str,
        log_file_open_format: str,
        file_log_level: int,
        date_format: str | None,
        max_bytes: int,
        backup_count: int,
    ) -> None:
        """
        Set up the file handler for logging.

        :param log_path: path to the log file.
        :param log_file_open_format: mode for opening the log file.
        :param file_log_level: logging level for the file handler.
        :param date_format: custom date format string.
        :param max_bytes: max size for rotation.
        :param backup_count: number of backups.
        """
        if not os.path.exists(log_path):
            try:
                with open(log_path, "w", encoding=self._encoding):
                    pass
            except IOError:
                pass

        use_date_format = date_format if date_format else self.DATE_FORMAT

        if self._json_format:
            fh_formatter = JSONFormatter(datefmt=use_date_format)
            # Use standard RotatingFileHandler for JSON to avoid padding
            file_handler = RotatingFileHandler(
                log_path,
                mode=log_file_open_format,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=self._encoding,
            )
        else:
            fh_formatter = logging.Formatter(self.LOG_FILE_FORMAT, use_date_format)
            file_handler = FormatLogLevelSpaces(
                log_path,
                mode=log_file_open_format,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=self._encoding,
            )

        fh_formatter.converter = self._time_converter

        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(fh_formatter)
        self.addHandler(file_handler)

    def _setup_console_handler(
        self,
        console_log_level: int,
        date_format: str | None,
    ) -> None:
        """
        Set up the console handler for logging.

        :param console_log_level: logging level for the console handler.
        :param date_format: custom date format string.
        """
        use_date_format = date_format if date_format else self.DATE_FORMAT

        if self._json_format:
            console_formatter = JSONFormatter(datefmt=use_date_format)
            console = logging.StreamHandler(stream=sys.stdout)
        else:
            console_formatter = logging.Formatter(self.FORMAT, use_date_format)
            console = ColoredConsoleHandler(stream=sys.stdout)

        console_formatter.converter = self._time_converter

        console.setLevel(console_log_level)
        console.setFormatter(console_formatter)
        self.addHandler(console)

    def get_log_file_path(self) -> str | None:
        """
        Get the path to the log file.

        :return: The log file path or None if not set.
        """
        return self._log_file_path

    def get_encoding(self) -> str:
        """
        Get the encoding used for the log file.

        :return: The encoding string (e.g., 'utf-8').
        """
        return self._encoding


if __name__ == "__main__":
    logger = Logger(__file__, log_file_path="test.log", json_format=True)
    # Basic log
    logger.info("Info message")

    # Bound log
    log = logger.bind(user_id=42, request_id="abc-123")
    log.warning("User action warning")
