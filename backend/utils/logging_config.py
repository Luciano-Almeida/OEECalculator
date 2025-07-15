# utils/logging_config.py

import os
from logging.config import dictConfig

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        },
        "console_simplificado": {
            "format": "%(message)s - %(name)s",
        },
        "json": {
            "format": (
                '{"timestamp": "%(asctime)s", '
                '"level": "%(levelname)s", '
                '"logger": "%(name)s", '
                '"message": "%(message)s"}'
            ),
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console_simplificado",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",  # Logs legíveis em arquivo
            "level": "INFO",
            "filename": f"{LOG_DIR}/app.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
            "encoding": "utf-8",
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",  # Logs em JSON
            "level": "INFO",
            "filename": f"{LOG_DIR}/app.json.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },

    "root": {
        "level": "DEBUG",
        #"handlers": ["json_file"],  # Para Produção
        "handlers": ["console", "file"],
    },
}
