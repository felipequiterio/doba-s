import logging
from colorama import init, Fore, Style

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
        log_level = f"[{record.name} {record.levelname}]"
        log_msg = super().format(record)
        return f"{log_color}{log_level}{Style.RESET_ALL} {log_msg}"

def get_custom_logger(name):
    logger = logging.getLogger(name)

    if not logger.handlers:  # Verifica se o logger já possui handlers
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = CustomFormatter('%(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger
