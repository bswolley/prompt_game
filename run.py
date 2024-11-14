# run.py
import os
import json
import logging
from src.app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Debug environment variables
logger.debug("Checking environment variables...")
groq_key = os.getenv('GROQ_API_KEY')
if groq_key:
    logger.debug("GROQ_API_KEY is set - first 4 chars: " + groq_key[:4] + "...")
else:
    logger.error("GROQ_API_KEY is NOT set!")