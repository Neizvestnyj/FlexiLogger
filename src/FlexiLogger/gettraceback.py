import os
import sys
import traceback
from traceback import FrameSummary
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logger import Logger
else:
    try:
        from .logger import Logger
    except ImportError:
        from logger import Logger


class GetTraceback:
    """
    A class to handle exception traceback extraction and logging.
    Allows saving tracebacks to a separate file or the main log.
    """

    def __init__(self, logger: Logger, log_file_path: str | None = None):
        """
        Initialize the GetTraceback handler.

        :param logger: FlexiLogger Logger instance.
        :param log_file_path: The path to the log file where traceback logs will be written.
                              If None, uses LOG_TRACEBACK_PATH env var or falls back to logger's file.
        """
        if not isinstance(logger, Logger) and not hasattr(logger, "get_log_file_path"):
            pass

        self.logger = logger

        if log_file_path:
            self._log_file_path = log_file_path
        elif os.getenv("LOG_TRACEBACK_PATH") is not None:
            self._log_file_path = os.getenv("LOG_TRACEBACK_PATH")
        else:
            self._log_file_path = self.logger.get_log_file_path()

        if self._log_file_path and self._log_file_path.lower() != "false":
            if not os.path.exists(self._log_file_path):
                self._log_mode = "w"
            else:
                self._log_mode = "a"

            self._encoding = self.logger.get_encoding()
        else:
            self._log_file_path = None

    def _get_traceback(self, text: str, print_full_exception: bool = True) -> tuple[bool, FrameSummary | None, str]:
        """
        Extracts traceback information and logs it.

        :param text: Custom error message to prepend.
        :param print_full_exception: Whether to print the full exception to stderr via traceback.print_exception.
        :return: A tuple containing a boolean indicating success, the extracted traceback frame, and the log text.
        """

        get_line_error = False
        extracted_tb: FrameSummary | None = None

        try:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            if exc_tb:
                extracted_tb_list = traceback.extract_tb(exc_tb)
                if extracted_tb_list:
                    extracted_tb = extracted_tb_list[0]
                    get_line_error = True

                if print_full_exception:
                    traceback.print_exception(exc_type, exc_obj, exc_tb)

        except Exception as get_line_except_error:
            self.logger.warning(f"Error extracting traceback: {get_line_except_error}")
            get_line_error = False
            extracted_tb = None

        if get_line_error:
            self.__write_traceback_to_file()

        log_text = self.__get_log_text(get_line_error, text, extracted_tb)

        return get_line_error, extracted_tb, log_text

    def __write_traceback_to_file(self) -> None:
        """
        Writes the traceback to the separate log file if configured.
        """
        if self._log_file_path:
            try:
                with open(self._log_file_path, self._log_mode, encoding=self._encoding) as log_file:
                    traceback.print_exc(file=log_file)
            except IOError as e:
                self.logger.error(f"Failed to write traceback to file: {e}")

    @staticmethod
    def __get_log_text(get_line_error: bool, text: str, tb: FrameSummary | None) -> str:
        """
        Constructs the log text based on the traceback and provided message.

        :param get_line_error: Indicates whether traceback extraction was successful.
        :param text: The message to log.
        :param tb: The extracted traceback frame summary, if available.
        :return: The formatted log text string.
        """

        log_text = f"{text} in line - {tb.lineno}" if get_line_error and tb is not None else f"{text}"

        return log_text

    def warning(self, text: str, print_full_exception: bool = False) -> None:
        """
        Logs a warning message with traceback information.

        :param text: The warning message to log.
        :param print_full_exception: Whether to print the full exception details to standard error.
        """
        _, _, log_text = self._get_traceback(text, print_full_exception)
        self.logger.warning(log_text)

    def error(self, text: str, print_full_exception: bool = False) -> None:
        """
        Logs an error message with traceback information.

        :param text: The error message to log.
        :param print_full_exception: Whether to print the full exception details to standard error.
        """
        _, _, log_text = self._get_traceback(text, print_full_exception)
        self.logger.error(log_text)

    def critical(self, text: str, print_full_exception: bool = False) -> None:
        """
        Logs a critical message with traceback information.

        :param text: The critical message to log.
        :param print_full_exception: Whether to print the full exception details to standard error.
        """
        _, _, log_text = self._get_traceback(text, print_full_exception)
        self.logger.critical(log_text)


def _test(get_traceback: GetTraceback) -> None:
    """
    Test function to log different levels of messages.

    :param get_traceback: An instance of GetTraceback to test.
    """

    get_traceback.warning("Warning")
    get_traceback.error("Error")
    get_traceback.critical("Critical")
