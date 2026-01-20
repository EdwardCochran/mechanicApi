from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from .extensions import db, ma, migrate, cache, limiter

def create_app(config_name="DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")
    if config_name == "ProductionConfig":
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            raise RuntimeError("DATABASE_URL (or SQLALCHEMY_DATABASE_URI) is not set")
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY is not set")

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)
    with app.app_context():
        db.create_all()

    # Swagger UI setup
    SWAGGER_URL = "/api/docs"
    API_URL = "/static/swagger.yaml"
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={"app_name": "Mechanic Shop API"},
    )

    # --- Import models so tables register ---
    from .models import Customer, Mechanic, ServiceTicket, Inventory  # noqa

    # --- Register blueprints ---
    from .Blueprints.customers.routes import customers_bp
    from .Blueprints.mechanics.routes import mechanic_bp
    from .Blueprints.service_tickets.routes import service_tickets_bp
    from .Blueprints.inventory.routes import inventory_bp

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
