import os
import logging
from flask_migrate import Migrate
from src.app import app, db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Checking environment variables...")

# GROQ_API_KEY Check
groq_key = os.getenv('GROQ_API_KEY')
if groq_key:
    logger.debug("GROQ_API_KEY is set - first 4 chars: " + groq_key[:4] + "...")
else:
    logger.error("GROQ_API_KEY is NOT set!")

# Use config from app.py which already handles environment switching
migrate = Migrate(app, db)
logger.debug(f"SQLAlchemy URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)