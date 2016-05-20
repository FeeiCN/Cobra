# coding: utf-8
import sys
import os
import ConfigParser

from flask import Flask
from flask.ext.script import Manager, Server
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import MigrateCommand, Migrate

from utils import log


log.info('Initialization HTTP Server')
reload(sys)
sys.setdefaultencoding('utf-8')

template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
asset = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/asset')
web = Flask(__name__, template_folder=template, static_folder=asset)

config = ConfigParser.ConfigParser()
config.read('config')
web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
web.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'mysql')

db = SQLAlchemy(web)

# just use the migration script's app context when you import the models
# http://stackoverflow.com/questions/33905706/flask-migrate-seemed-to-delete-all-my-database-data
with web.app_context():
    from models import *

migrate = Migrate(web, db)
manager = Manager(web)

host = config.get('cobra', 'host')
port = config.get('cobra', 'port')
port = int(port)

manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host=host, port=port))

from app import route
log.info('Cobra HTTP Server Started')


