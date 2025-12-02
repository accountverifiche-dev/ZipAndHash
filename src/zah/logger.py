import logging
import getpass
import sys
from typing import Optional
try:
    import colorama
except ImportError: # pragma: no cover
    colorama = None # pragma: no cover
else:
    colorama.init()


__all__ = ["setup_logging", "username"]


username = getpass.getuser().upper()


class _UserFilter(logging.Filter):
    """
    A logging filter that adds a username attribute to log records.

    This class extends the `logging.Filter` to modify the log record
    by adding a custom 'username' attribute. This can be useful for
    including user-specific information in log messages.

    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.username = username
        return True


class _ColorFormatter(logging.Formatter):
    """
    A formatter for log messages that applies color formatting based on log levels.

    This class inherits from `logging.Formatter` and provides additional
    functionality to format log messages with colored output. Each log level
    is assigned a specific color to improve readability and differentiation
    of log messages. The colors are applied using ANSI escape sequences, which
    makes the class particularly suited for terminal-based logging.

    :ivar RESET: ANSI escape sequence to reset any applied color.
    :type RESET: str
    :ivar COLORS: Mapping of log levels to their respective ANSI color codes.
    :type COLORS: dict[int, str]
    """
    RESET = "\x1b[0m"
    COLORS = {
        logging.DEBUG:      "\x1b[90m",     # grey
        logging.INFO:       "",             # default
        logging.WARNING:    "\x1b[33m",     # yellow
        logging.ERROR:      "\x1b[31m",     # red
        logging.CRITICAL:   "\x1b[1;32m"    # green
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the provided log record and applies color codes based on
        the log level. If a matching color is not found for the log level,
        the original message is returned without any color formatting.

        :param record: The log record object containing logging information.
        :type record: logging.LogRecord
        :return: The formatted and optionally color-coded log message.
        :rtype: str
        """
        msg = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        if not color:
            return msg
        return f"{color}{msg}{self.RESET}"


def setup_logging(debug: bool, log_file: Optional[str] = None) -> None:
    """
    Sets up logging configuration for the application.

    This function initializes the logging system with given settings, enabling
    logging to the console and optionally to a file in a specified format. It
    supports debug and info level logging, applies custom formatters, and
    filters logs using a user-defined filter mechanism. The debug flag determines
    the verbosity of logging, while the log_file parameter allows writing
    to a specified log file.

    :param debug: A boolean flag to set the logging level. If True, the logging
        level is set to DEBUG; otherwise it is set to INFO.
    :param log_file: Optional; A string representing the path to the file where
        log entries will be written. If None, logging to a file is disabled.
    :return: None
    """
    level = logging.DEBUG if debug else logging.INFO

    file_fmt = "%(asctime)s %(username)-10s | %(levelname)-8s > %(message)s"
    datefmt = "%Y/%m/%d-%H:%M:%S"
    file_formatter = logging.Formatter(file_fmt, datefmt=datefmt)

    stdout_formatter = _ColorFormatter("%(message)s")

    logging.basicConfig(level=level, handlers=[])
    root = logging.getLogger()
    root.setLevel(level)

    user_filter = _UserFilter()

    h_out = logging.StreamHandler(sys.stdout)
    h_out.setLevel(level)
    h_out.setFormatter(stdout_formatter)
    h_out.addFilter(user_filter)
    root.addHandler(h_out)

    if log_file:    # pragma: no cover
        h_file = logging.FileHandler(log_file)
        h_file.setLevel(level)
        h_file.setFormatter(file_formatter)
        h_file.addFilter(user_filter)
        root.addHandler(h_file)
