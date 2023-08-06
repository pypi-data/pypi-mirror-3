from cStringIO import StringIO
import logging


def setUpLogging(logger, level=logging.DEBUG):
    buf = StringIO()
    handler = logging.StreamHandler(buf)
    handler._added_by_tests_ = True
    handler._old_propagate_ = logger.propagate
    handler._old_level_ = logger.level
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(level)
    return buf


def tearDownLogging(logger):
    for handler in logger.handlers:
        if hasattr(handler, '_added_by_tests_'):
            logger.removeHandler(handler)
            logger.propagate = handler._old_propagate_
            logger.setLevel(handler._old_level_)
            break

