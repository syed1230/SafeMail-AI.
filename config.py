import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    TESTING = False
    MODEL_DIR = os.path.join(basedir, "model")

class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False

class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
