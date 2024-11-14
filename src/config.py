# src/config.py
import os
import json

from pathlib import Path

# Get base directory
BASE_DIR = Path(__file__).parent.parent

class Config:
    DEBUG = False
    TESTING = False
    CORS_HEADERS = 'Content-Type'
    TEMPLATES_AUTO_RELOAD = True
    
    # Template directory configuration
    TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
    
    # Dataset configuration file path
    DATASET_CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'datasets.json')
    
    # Data directory
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # API configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    MODEL_NAME = "llama3-70b-8192"
    TEMPERATURE = 0

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    
class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    
class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = 'testing'

# Function to get current config based on environment
def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    return config_map.get(env, DevelopmentConfig)