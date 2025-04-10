from flask import Flask
import config
import pytz
from middleware import ReverseProxied
from utils.time_utils import configure_timezone
from utils.ip_utils import configure_ip_detection
from db import db, init_db

# Create the Flask app
app = Flask(__name__, static_url_path='/static')
app.config['APPLICATION_ROOT'] = '/PuppyTracker'
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = config.SECRET_KEY

# Apply the middleware
app.wsgi_app = ReverseProxied(app.wsgi_app, script_name='/PuppyTracker')

# Initialize the database with the app
init_db(app)

# Configure timezone
timezone = configure_timezone(config.TIME_ZONE)

# Import models (after db initialization)
from models import Pet, PottyEvent, FoodEvent, SleepEvent, WalkEvent

# Initialize IP detection
configure_ip_detection(app)

# Import routes and register them
from routes.main_routes import register_main_routes
from routes.event_routes import register_event_routes
from routes.report_routes import register_report_routes
from routes.grid_routes import register_grid_routes

register_main_routes(app, db)
register_event_routes(app, db)
register_report_routes(app, db)
register_grid_routes(app, db)

# Initialize database
with app.app_context():
    db.create_all()
    # Create default pet if none exists
    pet = Pet.query.first()
    if not pet:
        from datetime import date
        default_pet = Pet(name="Tommo", birthdate=date(2025, 10, 3))
        db.session.add(default_pet)
        db.session.commit()

# Run the app if this file is executed directly
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    args = parser.parse_args()
    
    print(f"Starting Puppy Tracker application on {args.host}:{args.port}...")
    print(f"Debug mode: {config.DEBUG}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Using timezone: {config.TIME_ZONE}")
    print(f"Application URL: http://{args.host}:{args.port}{app.config['APPLICATION_ROOT']}")
    
    # Configure for trusted proxies
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['TRUSTED_PROXIES'] = ['127.0.0.1', '192.168.1.37/24', '10.0.0.1/24']
    
    app.run(host=args.host, port=args.port, debug=True)