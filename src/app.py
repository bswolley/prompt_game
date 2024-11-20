from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from pathlib import Path
import os
from dotenv import load_dotenv
from src.routes import api
from src.config import get_config
from src.models import db

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    config = get_config()
    
    # Create base directory path
    base_dir = Path(__file__).parent.parent
    
    # Create app with explicit static and template folders
    app = Flask(
        __name__,
        template_folder=base_dir / 'templates',
        static_folder=base_dir / 'static'  # Explicitly set static folder
    )
    
    # Load config
    app.config.from_object(config)
    print(f"SQLALCHEMY_DATABASE_URI from app config: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debug
    
    # Initialize database
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Setup CORS
    CORS(app)
    
    # Register blueprint
    app.register_blueprint(api)
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
