import os
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_DIR = Path(__file__).parent.parent

def load_environment():
    env_paths = [
        '.env',
        BASE_DIR / '.env',
        Path(os.getcwd()) / '.env'
    ]
    
    for env_path in env_paths:
        if os.path.exists(str(env_path)):
            load_dotenv(str(env_path))
            break
    else:
        logger.warning("No .env file found in expected locations.")

class Config:
    DEBUG = False
    TESTING = False
    CORS_HEADERS = 'Content-Type'
    TEMPLATES_AUTO_RELOAD = True
    
    TEMPLATE_DIR = str(BASE_DIR / 'templates')
    DATASET_CONFIG_PATH = str(BASE_DIR / 'config' / 'datasets.json')
    DATA_DIR = str(BASE_DIR / 'data')
    
    def __init__(self):
        load_environment()
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.MODEL_NAME = "llama3-70b-8192"
        self.TEMPERATURE = 0

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME')
        
        if os.getenv('LOCAL_DEVELOPMENT') == 'true':
            return f"postgresql+pg8000://{db_user}:{db_pass}@localhost:5433/{db_name}"
            
        instance_connection = '/cloudsql/prompt-wizards:europe-west1:leaderboard-db/.s.PGSQL.5432'
        return f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock={instance_connection}"

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///leaderboard.db'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    selected_config = config_map.get(env, DevelopmentConfig)()
    return selected_config