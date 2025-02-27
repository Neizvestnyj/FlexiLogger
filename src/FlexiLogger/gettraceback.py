import os
import sys
import traceback
from traceback import FrameSummary
from typing import Union

from .logger import Logger


class GetTraceback:
    def __init__(self, logger: Logger):
        """
        :param logger: FlexiLogger Logger class
        """
        self.logger = logger

    def _get_traceback(self, text: str, print_full_exception=True) -> tuple:
        """
        Extracts traceback information and logs it.

        :param text: Exception text (`except Exception as e`, e - our text)
        :param print_full_exception: Whether to print the full exception or just the provided text
        :return: A tuple containing a boolean indicating success, the extracted traceback, and the log text
        """

        try:
            get_line_error = True
            exc_type, exc_obj, exc_tb = sys.exc_info()

            extracted_tb = traceback.extract_tb(exc_tb)

            if extracted_tb and len(extracted_tb) > 0:
                extracted_tb = extracted_tb[0]

                if print_full_exception:
                    traceback.print_exception(exc_type, exc_obj, exc_tb)
            else:
                get_line_error = False
                extracted_tb = None
        except Exception as get_line_except_error:
            self.logger.warning(f"{get_line_except_error}")
            get_line_error = False
            extracted_tb = None

        if get_line_error:
            self.__write_traceback_to_file()

        log_text = self.__get_log_text(get_line_error, text, extracted_tb)

        return get_line_error, extracted_tb, log_text

    def __write_traceback_to_file(self) -> None:
        """
        Writes the traceback to the log file if `LOG_FILE` or `self.logger.log_file_path` is defined.
        """
        log_file_path = self.logger.get_log_file_path()
        if log_file_path and log_file_path.lower() != 'false':
            if not os.path.exists(log_file_path):
                mode = 'w'
            else:
                mode = 'a'
            with open(log_file_path, mode) as log_file:
                traceback.print_exc(file=log_file)

    @staticmethod
    def __get_log_text(get_line_error: bool, text: str, tb: Union[FrameSummary, None]) -> str:
        """
        Constructs the log text based on the traceback and provided message.

        :param get_line_error: Indicates whether traceback extraction was successful
        :param text: The message to log
        :param tb: The extracted traceback frame summary, if available
        :return: The formatted log text
        """

        if get_line_error:
            log_text = f"{text} in line - {tb[1]}"
        else:
            log_text = f"{text}"

        return log_text

    def warning(self, text: str, print_full_exception=False) -> None:
        """
        Logs a warning message with traceback information.

        :param text: The warning message to log
        :param print_full_exception: Whether to print the full exception or just the message
        """

        _, _, log_text = self._get_traceback(text, print_full_exception)
        self.logger.warning(log_text)

    def error(self, text: str, print_full_exception=False) -> None:
        """
        Logs an error message with traceback information.

        :param text: The error message to log
        :param print_full_exception: Whether to print the full exception or just the message
        """

        _, _, log_text = self._get_traceback(text, print_full_exception)
        self.logger.error(log_text)

    def critical(self, text: str, print_full_exception=False) -> None:
        """
        Logs a critical message with traceback information.

        :param text: The critical message to log
        :param print_full_exception: Whether to print the full exception or just the message
        """

        _, _, log_text = self._get_traceback(text, print_full_exception)
        self.logger.critical(log_text)


def _test(get_traceback: GetTraceback) -> None:
    """
    Test function to log different levels of messages.

    :param get_traceback: An instance of GetTraceback to test
    """

    get_traceback.warning('Warning')
    get_traceback.error('Error')
    get_traceback.critical('Critical')


if __name__ == '__main__':
    os.environ['LOG_FILE'] = 'false'
    get_traceback = GetTraceback(__file__)
    _test(get_traceback)
