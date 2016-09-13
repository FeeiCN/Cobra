import logging
from celery import Celery
from utils.third_party import Vulnerabilities
from utils import config

logging = logging.getLogger(__name__)

app = Celery('daemon', broker=config.Config('queue', 'broker').value, backend=config.Config('queue', 'backend').value)

"""
start client
celery -A daemon worker --loglevel=info
"""


@app.task
def push_vulnerabilities(vulnerabilities_info):
    v = Vulnerabilities()
    v.add(vulnerabilities_info)
    return v.push()


@app.task(bind=True)
def error_handler(self, uuid):
    result = self.app.AsyncResult(uuid)
    logging.critical('Task {0} raised exception: {1!r}\n{2!r}'.format(uuid, result.result, result.traceback))
