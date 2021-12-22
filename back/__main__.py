import os
import logging

from flask import Flask, send_from_directory
from flask_socketio import SocketIO

from .models import db, Setting
from .views import root


LOG_LEVEL = logging.getLevelName(os.environ.get('FLASK_LOG_LEVEL', 'ERROR').upper())
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(LOG_LEVEL)

HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', 5000))
DEBUG = os.environ.get('FLASK_DEBUG', '').lower() == 'true'
DB_PATH = os.environ.get('FLASK_DB_PATH', '/var/lib/db.sqlite3')

LOGGER.debug('using db: %s', DB_PATH)
app = Flask(__name__, static_url_path='/static/', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://%s' % DB_PATH
socketio = SocketIO(app)

# Set up urls and views.
app.add_url_rule('/', view_func=root)

db.init_app(app)
socketio.run(app, host=HOST, port=PORT, debug=DEBUG)