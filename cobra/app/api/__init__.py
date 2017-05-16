import logging
from flask import Flask
from flask_restful import Api
from .controller import *

logging = logging.getLogger(__name__)


def start(debug, host, port):
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Scan, '/scan')
    api.add_resource(Status, '/status/<string:job_id>')
    app.run(debug=debug, host=host, port=port, threaded=True, processes=1)
    logging.info('RESTful server start success')
