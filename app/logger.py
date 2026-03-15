import logging
import os
from pythonjsonlogger import jsonlogger


def setup_logger():
    # Use /var/log/webapp in production (EC2), fall back to local logs/ in CI/dev
    log_dir = "/var/log/webapp"
    try:
        os.makedirs(log_dir, exist_ok=True)
    except PermissionError:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
        os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    logger = logging.getLogger("webapp")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # File handler — this is what CloudWatch Agent reads
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler — for local dev and CI
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
