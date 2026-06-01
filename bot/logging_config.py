import logging
import os
import sys

def setup_logging(log_file: str = "bot.log") -> None:
    """
    Configures the application logging.
    Logs are written to the specified log_file with structured format and timestamps.
    Errors will include stack traces.
    """
    # Create formatter
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    formatter = logging.Formatter(log_format)

    # Base directory check - ensure logs folder exists if path includes directory
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # File Handler for bot.log (logs all INFO and above)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console Handler (typically we show warnings/errors on stdout/stderr, keeping CLI clean)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # Configure root logger or our specific package logger
    logger = logging.getLogger("binance_bot")
    logger.setLevel(logging.DEBUG)  # Capture everything, handlers will filter
    
    # Remove existing handlers to avoid duplicate logs if re-initialized
    logger.handlers = []
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Prevent propagation to the root logger to avoid duplicated logs in console
    logger.propagate = False

    logger.info("Logging initialized. Writing to %s", os.path.abspath(log_file))
