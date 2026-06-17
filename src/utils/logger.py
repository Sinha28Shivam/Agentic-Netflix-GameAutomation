import os
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it does not exist
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
os.makedirs(LOGS_DIR, exist_ok=True)

AUTOMATION_LOG_FILE = os.path.join(LOGS_DIR, "automation.log")
TELEMETRY_LOG_FILE = os.path.join(LOGS_DIR, "telemetry.log")

# Setup formatter
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)

def configure_logger(logger_name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Utility to configure a rotating file logger and console handler.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if logger is re-initialized
    if not logger.handlers:
        # File Handler (rotating at 10MB)
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

# Pre-configured loggers
automation_logger = configure_logger("automation", AUTOMATION_LOG_FILE)
telemetry_logger = configure_logger("telemetry", TELEMETRY_LOG_FILE)
