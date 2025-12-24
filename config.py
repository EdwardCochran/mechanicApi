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
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://user:password@localhost/mechanic_db"
    DEBUG = False
