import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get base directory
BASE_DIR = Path(__file__).parent.parent

def load_environment():
    """Load environment variables from .env files in potential locations."""
    env_paths = [
        '.env',
        BASE_DIR / '.env',
        Path(os.getcwd()) / '.env'
    ]
    
    for env_path in env_paths:
        if os.path.exists(str(env_path)):
            load_dotenv(str(env_path))
            logger.debug(f"Environment loaded from: {env_path}")
            break
    else:
        logger.warning("No .env file found in expected locations.")

class Config:
    """Base configuration class."""
    DEBUG = False
    TESTING = False
    CORS_HEADERS = 'Content-Type'
    TEMPLATES_AUTO_RELOAD = True
    
    # Directory configurations
    TEMPLATE_DIR = str(BASE_DIR / 'templates')
    DATASET_CONFIG_PATH = str(BASE_DIR / 'config' / 'datasets.json')
    DATA_DIR = str(BASE_DIR / 'data')
    
    # Database configurations (default to SQLite if DATABASE_URL is not set)
    SQLALCHEMY_DATABASE_URI = (
        'postgresql+pg8000://leaderboard-user:beelabs24@localhost:5433/leaderboard'
        if os.environ.get('LOCAL_DEVELOPMENT')
        else 'postgresql+pg8000://leaderboard-user:beelabs24@/leaderboard?unix_sock=/cloudsql/prompt-wizards:europe-west1:leaderboard-db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IS_PRODUCTION = os.environ.get('GAE_ENV', '').startswith('standard')
    
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
                logger.warning("GROQ_API_KEY not set and not found in .env file.")
        
        self.MODEL_NAME = "llama3-70b-8192"
        self.TEMPERATURE = 0

class ProductionConfig(Config):
   DEBUG = False
   ENV = 'production'

   SQLALCHEMY_DATABASE_URI = (
    f"postgresql+pg8000://{os.getenv('DB_USER', 'leaderboard-user')}:"
    f"{os.getenv('DB_PASS', 'beelabs24')}@/"
    f"{os.getenv('DB_NAME', 'leaderboard')}"
    "?unix_sock=/cloudsql/prompt-wizards:europe-west1:leaderboard-db/.s.PGSQL.5432"
)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///leaderboard.db'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

def get_config():
    """Determine which configuration class to use based on FLASK_ENV."""
    env = os.getenv('FLASK_ENV', 'development')
    logger.debug(f"FLASK_ENV environment variable: {env}")
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    selected_config = config_map.get(env, DevelopmentConfig)()
    logger.debug(f"Selected configuration: {selected_config.__class__.__name__}")
    logger.debug(f"SQLALCHEMY_DATABASE_URI: {selected_config.SQLALCHEMY_DATABASE_URI}")
    
    return selected_config
