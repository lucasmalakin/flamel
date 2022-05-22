# -*- coding: utf-8 -*-

# standard modules
import logging
import logging.config


class LogManager(object):
    _logger = None

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "json": {
                "format": '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "logger_name": "%(filename)s:%(funcName)s:%(lineno)d", "log": "%(message)s"}',
                "datefmt": "%H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "level": "WARNING",
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            }
        },
    }

    @staticmethod
    def get_logger(log_name):
        logger_name = log_name

        if not LogManager._logger:
            logging.config.dictConfig(LogManager.LOGGING)
            LogManager._logger = logging.getLogger(logger_name)
        return LogManager._logger


if __name__ == "__main__":
    print("==== TEST MODE - {} ====".format(LogManager.__name__))

    logger = LogManager.get_logger(log_name="test_logger")

    logger.info("Info test message")
    logger.warning("Warning test message")
    logger.error("Error test message")
