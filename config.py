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
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI") or ""
    SQLALCHEMY_DATABASE_URI = (
        db_url.replace("postgres://", "postgresql+psycopg://", 1)
              .replace("postgresql://", "postgresql+psycopg://", 1)
        if db_url
        else None
    )

    DEBUG = False
    CACHE_TYPE = "SimpleCache"
    SECRET_KEY = os.environ.get("SECRET_KEY")
