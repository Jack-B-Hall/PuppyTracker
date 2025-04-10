from flask import render_template, redirect, url_for, request
from datetime import datetime
from models import Pet
from utils.ip_utils import get_client_ip
from user_settings import UserSettings

def register_main_routes(app, db):
    """Register main routes with the application."""
    
    @app.context_processor
    def inject_settings():
        # Get the IP address of the client
        client_ip = get_client_ip()
        # Get settings for this client
        user_settings = UserSettings.get_settings(client_ip)
        
        return {
            'app_name': app.config.get('APP_NAME', 'Puppy Tracker'),
            'app_version': app.config.get('APP_VERSION', '1.0'),
            'default_recorder': app.config.get('DEFAULT_RECORDER', 'Jack'),
            'second_recorder': app.config.get('SECOND_RECORDER', 'Lexy'),
            'user_settings': user_settings
        }
    
    @app.route('/')
    def index():
        from routes.event_routes import auto_end_walks
        # Auto-end walks that are past the threshold
        auto_end_walks(db)
        
        # Get the pet for display
        pet = Pet.query.first()
        return render_template('index.html', pet=pet)
    
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        pet = Pet.query.first()
        
        if request.method == 'POST':
            pet.name = request.form.get('name')
            birthdate_str = request.form.get('birthdate')
            pet.birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
            
            db.session.commit()
            return redirect(url_for('profile'))
        
        return render_template('profile.html', pet=pet)
    
    @app.route('/settings')
    def settings():
        return redirect(url_for('preferences'))
    
    @app.route('/preferences')
    def preferences():
        # Get the client's IP address
        client_ip = get_client_ip()
        
        # Get settings for this client
        user_settings = UserSettings.get_settings(client_ip)
        
        return render_template('preferences.html', user_settings=user_settings)
    
    @app.route('/save_preferences', methods=['POST'])
    def save_preferences():
        # Get the client's IP address
        client_ip = get_client_ip()
        
        # Process additional recorders from textarea
        additional_recorders = request.form.get('additional_recorders', '')
        
        # Create settings dictionary from form data
        settings = {
            "default_recorder": request.form.get('default_recorder'),
            "additional_recorders": additional_recorders,
            "food": {
                "amount": float(request.form.get('food_amount')),
                "type": request.form.get('food_type')
            },
            "walk": {
                "duration": int(request.form.get('walk_duration')),
                "auto_end_after": int(request.form.get('walk_auto_end'))
            },
            "sleep": {
                "bedtime": request.form.get('bed_time'),
                "wake_time": request.form.get('wake_time')
            },
            "last_updated": datetime.now().isoformat()
        }
        
        # Save settings for this client
        UserSettings.save_settings(client_ip, settings)
        
        return redirect(url_for('preferences'))