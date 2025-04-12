import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', 'localhost')
    
    # Database Configuration
    DB_CONFIG = {
        'username': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME')
    }
    
    # API Keys
    API_KEY = os.getenv('API_KEY') 