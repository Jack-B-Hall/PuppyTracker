from db import db
from datetime import datetime, date

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, default="Tommo")
    birthdate = db.Column(db.Date, nullable=False, default=date(2025, 10, 3))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pet {self.name}>'
    
    def age_in_months(self):
        today = date.today()
        return (today.year - self.birthdate.year) * 12 + today.month - self.birthdate.month

class PottyEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_type = db.Column(db.String(1), nullable=False)  # 'U' or 'D'
    is_accident = db.Column(db.Boolean, default=False)
    on_cue = db.Column(db.Boolean, default=False)
    recorded_by = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<PottyEvent {self.event_type} at {self.timestamp}>'

class FoodEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=True)  # in cups or your preferred unit
    food_type = db.Column(db.String(50), nullable=True)
    recorded_by = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<FoodEvent at {self.timestamp}>'

class SleepEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sleep_time = db.Column(db.DateTime, nullable=True)
    wake_time = db.Column(db.DateTime, nullable=True)
    recorded_by = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<SleepEvent {self.sleep_time} to {self.wake_time}>'

class WalkEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # in minutes
    recorded_by = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<WalkEvent at {self.start_time} for {self.duration} mins>'