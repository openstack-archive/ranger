import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.log_exception = lambda msg, exception: logger.exception(msg + " Exception: " + str(exception))

    return logger

__all__ = ['get_logger']
