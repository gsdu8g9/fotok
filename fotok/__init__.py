"""
This is an entry point for FotOK web app.
It loads all components and initializes Flask app.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)

app.config.from_object('fotok.config')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from .cache import create_cache

cache = create_cache(app.config['CACHE_KIND'], app.config)

from . import views, models, api
