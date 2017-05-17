import socket
import errno
from flask import Flask
from flask_restful import Api
from .controller import *
from utils.log import logger


def start(debug, host, port):
    logger.info('Start {host}:{port}'.format(host=host, port=port))
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Scan, '/scan')
    api.add_resource(Status, '/status/<string:job_id>')
    try:
        app.run(debug=debug, host=host, port=int(port), threaded=True, processes=1)
    except socket.error, v:
        if v[0] == errno.EACCES:
            logger.critical('must sudo permission for start RESTful server!')
            exit()
        else:
            logger.critical('{msg}'.format(msg=v[1]))

    logger.info('RESTful server start success')
