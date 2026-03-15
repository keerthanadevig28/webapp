import logging
import os
from pythonjsonlogger import jsonlogger


def setup_logger():
    # Create log directory if it doesn't exist
    os.makedirs("/var/log/webapp", exist_ok=True)

    logger = logging.getLogger("webapp")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # File handler — this is what CloudWatch Agent reads
    file_handler = logging.FileHandler("/var/log/webapp/app.log")
    file_handler.setLevel(logging.DEBUG)

    # Console handler — for local dev
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # JSON format so CloudWatch can parse it easily
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Single logger instance used across the whole app
logger = setup_logger()
