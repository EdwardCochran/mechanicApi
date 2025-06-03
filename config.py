class DevelopmentConfig:
    sqlalchemy_database_uri = 'mysql+mysqlconnector://root:power317@localhost/mechanic_db'
    DEBUG = True
    
class TestingConfig:
    pass
    
class ProductionConfig:
    pass    