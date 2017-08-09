from cobra.engine import scan
from cobra.config import examples_path
from cobra.log import logger


def test_scan():
    logger.info('Examples Path: {path}'.format(path=examples_path))
    assert scan(examples_path)
