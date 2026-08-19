import logging
import sys
from app.config.settings import get_settings

LOG_FORMAT = "[%(levelname)s] [%(name)s] %(message)s"


def setup_logging() -> None:
    """Configure root and component loggers."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if already configured
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(logging.Formatter(LOG_FORMAT))


def get_logger(name: str) -> logging.Logger:
    """Return a named logger conforming to standard application formatting."""
    setup_logging()
    return logging.getLogger(name)
