from flask_sqlalchemy import SQLAlchemy

# Create the database instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the application"""
    db.init_app(app)