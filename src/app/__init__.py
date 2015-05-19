from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.cache import Cache
from werkzeug.contrib.cache import SimpleCache
from flask.ext.moment import Moment
from config import config


bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
cache = Cache()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .transactions import transactions as transactions_blueprint
    app.register_blueprint(transactions_blueprint, url_prefix='/transactions')
    
    from .portfolio import portfolio as portfolio_blueprint
    app.register_blueprint(portfolio_blueprint)

    from .performance import performance as performance_blueprint
    app.register_blueprint(performance_blueprint)

    return app

