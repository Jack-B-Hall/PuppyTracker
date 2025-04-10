import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Base configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'puppy-tracker-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///pet_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application settings
    APP_NAME = "Puppy Tracker"
    APP_VERSION = "1.0.0"
    DEFAULT_RECORDER = "Jack"
    SECOND_RECORDER = "Lexy"
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))  # Changed default to 8080
    
    # Time zone settings (for display purposes)
    TIME_ZONE = os.getenv('TIME_ZONE', 'Australia/Adelaide')
    
    # Debug settings
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Make configuration accessible as module attributes
current_config = config['production']
SECRET_KEY = current_config.SECRET_KEY
SQLALCHEMY_DATABASE_URI = current_config.SQLALCHEMY_DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = current_config.SQLALCHEMY_TRACK_MODIFICATIONS
APP_NAME = current_config.APP_NAME
APP_VERSION = current_config.APP_VERSION
DEFAULT_RECORDER = current_config.DEFAULT_RECORDER
SECOND_RECORDER = current_config.SECOND_RECORDER
HOST = current_config.HOST
PORT = current_config.PORT
TIME_ZONE = current_config.TIME_ZONE
DEBUG = current_config.DEBUG