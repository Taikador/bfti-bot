# credits: https://github.com/python-discord/bot/blob/main/bot/log.py
import logging
from logging import handlers
from pathlib import Path
from sys import stdout

import coloredlogs

from .config import config


def setup() -> None:
    log_level = logging.INFO if config.debug else logging.WARN
    format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    log_format = logging.Formatter(format_string)

    log_file = Path("logs", "bot.log")
    log_file.parent.mkdir(exist_ok=True)
    file_handler = handlers.RotatingFileHandler(
        log_file, maxBytes=5242880, backupCount=7, encoding="utf8"
    )
    file_handler.setFormatter(log_format)

    root_log = logging.getLogger()
    root_log.setLevel(log_level)
    root_log.addHandler(file_handler)

    coloredlogs.DEFAULT_LEVEL_STYLES = {
        **coloredlogs.DEFAULT_LEVEL_STYLES,
        "trace": {"color": 246},
        "critical": {"background": "red"},
        "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"],
    }
    coloredlogs.DEFAULT_LOG_FORMAT = format_string
    coloredlogs.DEFAULT_LOG_LEVEL = log_level
    coloredlogs.install(logger=root_log, stream=stdout)
