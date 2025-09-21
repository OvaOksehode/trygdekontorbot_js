import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from config import settings

def setup_logging():
    env = settings.environment

    log_dir = os.path.join("logs", "testing" if env == "testing" else "dev")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"{datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}[{env}].log")
    log_level = logging.DEBUG if env == "testing" else logging.INFO

    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    )

    # Clear existing handlers
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    file_handler = RotatingFileHandler(log_file_path, maxBytes=10_000_000, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.info(f"Logging initialized for environment: {env}")
