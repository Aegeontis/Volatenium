import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

import numpy as np
import yaml


class CustomFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[90m",  # Gray
        "INFO": "\033[94m",  # Blue
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Purple
        "RESET": "\033[0m"  # Reset color
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        time = datetime.now().strftime("%Y-%b-%d %H:%M.%S")
        log_str = f"{color}[{record.levelname[0]}] {time} {record.getMessage()}{self.COLORS["RESET"]}"
        # Write uncolored log to file as well
        if hasattr(record, "logfile") and record.logfile:
            return f"[{record.levelname[0]}] {time} {record.getMessage()}"
        return log_str


def float_to_human_readable(number: float):
    return np.format_float_positional(number, trim='-')


def log_action(action_report: dict, exchange_name: str, algorithm_name: str):
    history = {}

    if not os.path.exists("cache"):
        os.makedirs("cache")
    if os.path.exists("cache/history.json"):
        with open("cache/history.json", "r") as f:
            history = json.load(f)

    if exchange_name not in history:
        history[exchange_name] = {}
    if algorithm_name not in history[exchange_name]:
        history[exchange_name][algorithm_name] = []
    history[exchange_name][algorithm_name].append({
        "unix_timestamp": action_report["unix_timestamp"],
        "id": action_report["id"],
        "action": action_report["action"],
        "action-result": action_report["action_result"],
        "transacted_amount": action_report["transacted_amount"],
        "current_price": action_report["current_price"],
        "crypto-wallet": action_report["wallet_crypto_amount"],
        "fiat-wallet": action_report["wallet_fiat_amount"]
    })

    with open("cache/history.json", "w") as f:
        json.dump(history, f, indent=4)
        # immediately write to disk
        f.flush()
        os.fsync(f.fileno())


def read_settings() -> dict:
    settings: dict = {}
    if os.path.exists("settings.yaml"):
        with open("settings.yaml", "r") as f:
            settings = yaml.safe_load(f)
    else:
        logger.error("settings.yaml not found. See README for more details. Exiting...")
        sys.exit(1)
    return settings


def store_settings(settings: dict):
    with open("settings.yaml", "w") as f:
        yaml.safe_dump(settings, f, indent=2)


def store_state(variables: dict):
    if not os.path.exists("cache"):
        os.makedirs("cache")
    with open("cache/state.yaml", "w") as f:
        yaml.safe_dump(variables, f, indent=2)
        # immediately write to disk
        f.flush()
        os.fsync(f.fileno())


def read_state() -> dict:
    cached_vars = {}
    if os.path.exists("cache/state.yaml"):
        with open("cache/state.yaml", "r") as f:
            cached_vars = yaml.safe_load(f)
    return cached_vars


# Create log directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger("custom_logger")
logger.setLevel(logging.DEBUG)

# Console handler for colored output
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

# Rotate log files on each run
fh = RotatingFileHandler(os.path.join(log_dir, "current.log"), maxBytes=1, backupCount=4)
fh.setFormatter(CustomFormatter())
logger.addHandler(fh)
