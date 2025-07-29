from flask import Flask
from .extensions import ma, limiter
from App.extensions import cache
from .Blueprints.customers import customers_bp
from .Blueprints.mechanics import mechanic_bp
from .Blueprints.service_tickets import service_tickets_bp
from .models import db

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')

    return app
