import logging
import sys
from pathlib import Path
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',     # cyan
        'INFO': '\033[32m',      # green
        'WARNING': '\033[33m',   # yellow
        'ERROR': '\033[31m',     # red
        'RESET': '\033[0m'
    }

    def format(self, record):
        message = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        return f"{color}{message}{self.COLORS['RESET']}"


def setup_logger(name, log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter('%(levelname)s: %(message)s'))
        logger.addHandler(console_handler)

        if log_file:
            log_path = Path.home() / ".janus-clew" / log_file
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(file_handler)

    return logger
