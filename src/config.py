# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Get base directory
BASE_DIR = Path(__file__).parent.parent

def load_environment():
    # Try multiple env file locations
    env_paths = [
        '.env',
        BASE_DIR / '.env',
        Path(os.getcwd()) / '.env'
    ]
    
    for env_path in env_paths:
        if os.path.exists(str(env_path)):
            load_dotenv(str(env_path))
            break

class Config:
    DEBUG = False
    TESTING = False
    CORS_HEADERS = 'Content-Type'
    TEMPLATES_AUTO_RELOAD = True
    
    # Directory configurations
    TEMPLATE_DIR = str(BASE_DIR / 'templates')
    DATASET_CONFIG_PATH = str(BASE_DIR / 'config' / 'datasets.json')
    DATA_DIR = str(BASE_DIR / 'data')
    
    def __init__(self):
        # Load environment variables
        load_environment()
        
        # API configuration
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        if not self.GROQ_API_KEY:
            # Fallback to direct file reading
            try:
                with open(BASE_DIR / '.env', 'r') as f:
                    for line in f:
                        if line.startswith('GROQ_API_KEY='):
                            self.GROQ_API_KEY = line.split('=')[1].strip()
                            break
            except Exception:
                pass
                 
        self.MODEL_NAME = "llama3-70b-8192"
        self.TEMPERATURE = 0

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

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    return config_map.get(env, DevelopmentConfig)()