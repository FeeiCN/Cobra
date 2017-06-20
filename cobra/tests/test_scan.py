from cobra.engine.scans import scan
from cobra.utils.config import examples_path
from cobra.utils.log import logger


def test_scan():
    logger.info('Examples Path: {path}'.format(path=examples_path))
    scan(examples_path)
    assert False
