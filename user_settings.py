import json
import os
from datetime import datetime

class UserSettings:
    SETTINGS_FILE = 'user_settings.json'
    
    @staticmethod
    def get_settings(ip_address):
        """Retrieve settings for a specific IP address"""
        if not os.path.exists(UserSettings.SETTINGS_FILE):
            return UserSettings.get_default_settings()
        
        try:
            with open(UserSettings.SETTINGS_FILE, 'r') as f:
                all_settings = json.load(f)
            
            # Return settings for this IP or default settings if not found
            return all_settings.get(ip_address, UserSettings.get_default_settings())
        except Exception as e:
            print(f"Error loading user settings: {e}")
            return UserSettings.get_default_settings()
    
    @staticmethod
    def save_settings(ip_address, settings):
        """Save settings for a specific IP address"""
        all_settings = {}
        
        # Load existing settings if file exists
        if os.path.exists(UserSettings.SETTINGS_FILE):
            try:
                with open(UserSettings.SETTINGS_FILE, 'r') as f:
                    all_settings = json.load(f)
            except Exception as e:
                print(f"Error loading existing settings: {e}")
        
        # Process additional recorders from textarea (one per line)
        if 'additional_recorders' in settings and isinstance(settings['additional_recorders'], str):
            # Split by newlines and remove empty lines
            recorders = [r.strip() for r in settings['additional_recorders'].split('\n') if r.strip()]
            settings['additional_recorders'] = recorders
        
        # Update settings for this IP
        all_settings[ip_address] = settings
        
        # Save back to file
        try:
            with open(UserSettings.SETTINGS_FILE, 'w') as f:
                json.dump(all_settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user settings: {e}")
            return False
    
    @staticmethod
    def get_default_settings():
        """Get default settings for new users"""
        return {
            "default_recorder": "Jack",
            "additional_recorders": ["Lexy"],
            "food": {
                "amount": 1.5,
                "type": "Kibble"
            },
            "walk": {
                "duration": 30,  # minutes
                "auto_end_after": 120  # minutes (2 hours)
            },
            "sleep": {
                "bedtime": "22:00",  # 10:00 PM
                "wake_time": "08:00"  # 8:00 AM
            },
            "last_updated": datetime.now().isoformat()
        }