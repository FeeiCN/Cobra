from flask import request
from flask_restful import Resource


class Scan(Resource):
    def put(self):
        token = request.form['token']
        return {'hello': 'world'}


class Status(Resource):
    def get(self, job_id):
        return {job_id: 'running'}
