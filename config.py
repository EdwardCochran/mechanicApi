class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:power317@localhost/mechanic_db'
    DEBUG = True
    
class TestingConfig:
    pass
    
class ProductionConfig:
    pass    