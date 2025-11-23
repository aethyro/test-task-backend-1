import logging
import logging.config

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    level = settings.logging_level

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(name)s] "
                    "%(message)s (%(filename)s:%(lineno)d)",
                },
                "uvicorn_access": {
                    "format": "%(asctime)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": "DEBUG",
                },
                "uvicorn_console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": "INFO",
                },
                "uvicorn_access_console": {
                    "class": "logging.StreamHandler",
                    "formatter": "uvicorn_access",
                    "level": "INFO",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["uvicorn_console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["uvicorn_console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["uvicorn_access_console"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
        }
    )
