from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.logger import Logger

logger = Logger().get_logger()

# Load environment variables
load_dotenv()

def create_app():
    logger.info("Initializing Flask application...")
    app = Flask(__name__)
    CORS(app)
    
    # Configure template directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app.template_folder = template_dir
    
    # Import routes after app initialization
    try:
        from routes import api
        app.register_blueprint(api)
        
        # Basic health check
        @app.route('/_ah/warmup')
        def warmup():
            return '', 200
            
        logger.info(f"Application initialized on port: {os.environ.get('PORT', '8080')}")
    except Exception as e:
        logger.critical(f"Failed to initialize application: {e}", exc_info=True)
        raise
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
