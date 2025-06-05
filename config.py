class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:power317@localhost/mechanic_db'
    DEBUG = True
    CACHE_Type = 'SimpleCache'
    CACHE_Default_Timeout = 300
class TestingConfig:
    pass
    
class ProductionConfig:
    pass    