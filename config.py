class Config:
    DEBUG = False
    TESTING = False
    CORS_HEADERS = 'Content-Type'

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True