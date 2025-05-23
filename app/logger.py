import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging format
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Configure file handler
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=10_000_000, backupCount=5  # 10MB
)
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.INFO)

# Configure console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Add handlers if they haven't been added before
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
