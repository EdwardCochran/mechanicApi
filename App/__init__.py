from flask import Flask
from .extensions import ma, limiter
from App.extensions import cache
from .Blueprints.customers import customers_bp
from .Blueprints.mechanics import mechanic_bp
from .Blueprints.service_tickets.routes import service_ticket_bp
from .models import db


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service_tickets')
    
    return app