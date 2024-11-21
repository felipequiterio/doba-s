import logging
import inspect
from colorama import init, Fore, Style
from pathlib import Path

init(autoreset=True)


class CustomFormatter(logging.Formatter):
    LOG_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        log_color = self.LOG_COLORS.get(record.levelno)

        # Get the caller's frame information
        frame = inspect.currentframe()
        # Go back 3 frames to get the actual caller (adjust if needed)
        for _ in range(3):
            if frame.f_back:
                frame = frame.f_back

        # Extract file path and convert to relative path
        file_path = Path(frame.f_code.co_filename).relative_to(Path.cwd())
        func_name = frame.f_code.co_name
        line_no = frame.f_lineno

        # Format the location info
        location = f"{file_path}:{line_no} in {func_name}()"

        # Format the log header with module name and level
        log_header = f"[{record.name} {record.levelname}]"

        # Format the full message
        if record.exc_info:
            # If there's an exception, include it in the message
            exc_info = self.formatException(record.exc_info)
            full_message = f"{log_color}{log_header}{Style.RESET_ALL} {location}\n{record.getMessage()}\n{exc_info}"
        else:
            full_message = f"{log_color}{log_header}{Style.RESET_ALL} {location}\n{record.getMessage()}"

        return full_message


def get_custom_logger(name):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = CustomFormatter()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Optional: File Handler for persistent logging
        file_handler = logging.FileHandler("app.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Optional: Add a function to log exceptions with full traceback
def log_exception(logger, message, exc_info=True):
    """
    Helper function to log exceptions with full traceback
    """
    logger.error(message, exc_info=exc_info)
