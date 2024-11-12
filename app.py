# app.py
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from routes import api

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    CORS(app)
    
    # Configure template directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app.template_folder = template_dir
    
    # Register blueprint
    app.register_blueprint(api)
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)