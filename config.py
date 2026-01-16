import os


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:power317@localhost/mechanic_db"
    DEBUG = True

    # Flask Cache Configuration
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # Secret Key
    SECRET_KEY = "CHANGE-ME"
    JWT_ALGORITHM = "HS256"

    # Rate limiting configuration
    RATELIMIT_DEFAULT = "200 per day"


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True


class ProductionConfig:
    db_url = os.environ.get("SQLALCHEMY_DATABASE_URI") or os.environ.get("DATABASE_URL")
    if db_url:
        SQLALCHEMY_DATABASE_URI = (
            db_url.replace("postgres://", "postgresql+psycopg2://", 1)
                  .replace("postgresql://", "postgresql+psycopg2://", 1)
        )
    DEBUG = False
    CACHE_TYPE = "SimpleCache"
