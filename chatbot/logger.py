# logger.py
# Handles all logging for the chatbot — saves every interaction to a log file.

import logging
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "logs", "chat_logs.txt")


def setup_logger():
    """Configure and return the chatbot logger."""
    logger = logging.getLogger("NLI_Manufacturing")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # File handler — saves everything
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Console handler — only warnings and above
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def log_interaction(logger, user_input, response, response_time_ms, matched):
    """Log a single chatbot interaction with full details."""
    status = "MATCHED" if matched else "UNMATCHED"
    logger.info(
        f"[{status}] Input: '{user_input}' | "
        f"Response: '{response[:60]}...' | "
        f"Time: {response_time_ms:.2f}ms"
    )