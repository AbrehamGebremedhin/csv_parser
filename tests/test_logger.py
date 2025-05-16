import logging
import pytest
from app.utils.logger import Logger


def test_logger_singleton():
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2


def test_logger_methods(caplog):
    logger = Logger()
    with caplog.at_level(logging.INFO):
        logger.info('info message')
    assert 'info message' in caplog.text

    with caplog.at_level(logging.ERROR):
        logger.error('error message')
    assert 'error message' in caplog.text

    with caplog.at_level(logging.WARNING):
        logger.warning('warning message')
    assert 'warning message' in caplog.text

    with caplog.at_level(logging.DEBUG):
        logger.debug('debug message')
    # DEBUG logs may not be captured if logger level is INFO by default
    # So, temporarily set logger level to DEBUG
    logger.logger.setLevel(logging.DEBUG)
    logger.debug('debug message')
    assert 'debug message' in caplog.text
    logger.logger.setLevel(logging.INFO)

    with caplog.at_level(logging.CRITICAL):
        logger.critical('critical message')
    logger.logger.setLevel(logging.CRITICAL)
    logger.critical('critical message')
    assert 'critical message' in caplog.text
    logger.logger.setLevel(logging.INFO)
