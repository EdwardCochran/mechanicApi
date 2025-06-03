from flask import Flask
from .extensions import ma, db
# from .models import db, Customer
from .Blueprints.Customers import customers_bp
from .Blueprints.mechanics import mechanic_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    
    return app