from flask import request, redirect, url_for
from datetime import datetime, timedelta
from models import PottyEvent, FoodEvent, SleepEvent, WalkEvent
from utils.time_utils import get_local_time
from utils.ip_utils import get_client_ip
from user_settings import UserSettings

def auto_end_walks(db):
    """Automatically end walks that have exceeded the threshold duration."""
    try:
        # Find the latest walk events without an end time
        unfinished_walks = WalkEvent.query.filter(WalkEvent.end_time.is_(None)).all()
        
        now = get_local_time()
        for walk in unfinished_walks:
            # Get user settings for this recorder
            settings = UserSettings.get_default_settings()  # Use default as fallback
            
            # Calculate time since walk started
            walk_duration = (now - walk.start_time).total_seconds() / 60  # in minutes
            
            # If past the auto-end threshold, end the walk
            if walk_duration > settings['walk']['auto_end_after']:
                walk.end_time = now
                walk.duration = int(walk_duration)
                walk.notes = (walk.notes or "") + f" (Auto-ended after {settings['walk']['auto_end_after']} minutes)"
                db.session.commit()
    except Exception as e:
        print(f"Error in auto_end_walks: {e}")

def register_event_routes(app, db):
    """Register event CRUD routes with the application."""
    
    # === Event Creation Routes ===
    
    @app.route('/add_potty_event', methods=['POST'])
    def add_potty_event():
        event_type = request.form.get('event_type')
        potty_status = request.form.get('potty_status', 'on_cue')
        is_accident = (potty_status == 'accident')
        on_cue = (potty_status == 'on_cue')
        recorded_by = request.form.get('recorded_by')
        notes = request.form.get('notes', '')
        
        # Handle custom time if provided
        if request.form.get('use_custom_time') == 'yes':
            custom_time_str = request.form.get('custom_time')
            timestamp = datetime.strptime(custom_time_str, '%Y-%m-%dT%H:%M')
        else:
            timestamp = get_local_time()
        
        event = PottyEvent(
            timestamp=timestamp,
            event_type=event_type,
            is_accident=is_accident,
            on_cue=on_cue,
            recorded_by=recorded_by,
            notes=notes
        )
        
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('index'))
    
    @app.route('/add_food_event', methods=['POST'])
    def add_food_event():
        amount = request.form.get('amount')
        food_type = request.form.get('food_type')
        recorded_by = request.form.get('recorded_by')
        notes = request.form.get('notes', '')
        
        # Handle custom time if provided
        if request.form.get('use_custom_time') == 'yes':
            custom_time_str = request.form.get('custom_time')
            timestamp = datetime.strptime(custom_time_str, '%Y-%m-%dT%H:%M')
        else:
            timestamp = get_local_time()
        
        event = FoodEvent(
            timestamp=timestamp,
            amount=amount if amount else None,
            food_type=food_type,
            recorded_by=recorded_by,
            notes=notes
        )
        
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('index'))
    
    @app.route('/add_sleep_event', methods=['POST'])
    def add_sleep_event():
        event_type = request.form.get('sleep_type')
        recorded_by = request.form.get('recorded_by')
        notes = request.form.get('notes', '')
        
        # Handle custom time if provided
        if request.form.get('use_custom_time') == 'yes':
            custom_time_str = request.form.get('custom_time')
            timestamp = datetime.strptime(custom_time_str, '%Y-%m-%dT%H:%M')
        else:
            timestamp = get_local_time()
        
        if event_type == 'sleep':
            event = SleepEvent(
                sleep_time=timestamp,
                wake_time=None,
                recorded_by=recorded_by,
                notes=notes
            )
        else:  # wake
            # Find the latest sleep event without a wake time
            last_sleep = SleepEvent.query.filter(SleepEvent.wake_time.is_(None)).order_by(SleepEvent.sleep_time.desc()).first()
            
            if last_sleep:
                last_sleep.wake_time = timestamp
                db.session.commit()
                return redirect(url_for('index'))
            else:
                # If no matching sleep event, create a new sleep event using default settings
                user_settings = UserSettings.get_settings(get_client_ip())
                
                # Parse default bedtime (e.g., "22:00")
                bedtime_parts = user_settings['sleep']['bedtime'].split(':')
                bedtime_hour = int(bedtime_parts[0])
                bedtime_minute = int(bedtime_parts[1])
                
                # Create a timestamp for last night at the default bedtime
                yesterday = timestamp.date() - timedelta(days=1)
                default_sleep_time = datetime.combine(yesterday, datetime.min.time().replace(hour=bedtime_hour, minute=bedtime_minute))
                
                event = SleepEvent(
                    sleep_time=default_sleep_time,
                    wake_time=timestamp,
                    recorded_by=recorded_by,
                    notes=f"Sleep time automatically set to default bedtime. {notes}"
                )
        
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('index'))
    
    @app.route('/add_walk_event', methods=['POST'])
    def add_walk_event():
        event_type = request.form.get('walk_type')
        recorded_by = request.form.get('recorded_by')
        notes = request.form.get('notes', '')
        
        # Handle custom time if provided
        if request.form.get('use_custom_time') == 'yes':
            custom_time_str = request.form.get('custom_time')
            timestamp = datetime.strptime(custom_time_str, '%Y-%m-%dT%H:%M')
        else:
            timestamp = get_local_time()
        
        if event_type == 'start':
            event = WalkEvent(
                start_time=timestamp,
                end_time=None,
                duration=None,
                recorded_by=recorded_by,
                notes=notes
            )
            db.session.add(event)
        else:  # end
            # Find the latest walk event without an end time
            last_walk = WalkEvent.query.filter(WalkEvent.end_time.is_(None)).order_by(WalkEvent.start_time.desc()).first()
            
            if last_walk:
                last_walk.end_time = timestamp
                # Calculate duration in minutes
                duration = int((last_walk.end_time - last_walk.start_time).total_seconds() / 60)
                last_walk.duration = duration
                db.session.commit()
                return redirect(url_for('index'))
            else:
                # If no matching start event, create a new walk with estimated start time
                user_settings = UserSettings.get_settings(get_client_ip())
                default_duration = user_settings['walk']['duration']
                estimated_start_time = timestamp - timedelta(minutes=default_duration)
                
                event = WalkEvent(
                    start_time=estimated_start_time,
                    end_time=timestamp,
                    duration=default_duration,
                    recorded_by=recorded_by,
                    notes=f"Start time automatically set ({default_duration} min walk). {notes}"
                )
                db.session.add(event)
        
        db.session.commit()
        return redirect(url_for('index'))
    
    # === Event Editing Routes ===
    
    @app.route('/edit_potty_event', methods=['POST'])
    def edit_potty_event():
        event_id = request.form.get('event_id')
        event = PottyEvent.query.get_or_404(event_id)
        
        event.event_type = request.form.get('event_type')
        
        potty_status = request.form.get('potty_status', 'on_cue')
        event.is_accident = (potty_status == 'accident')
        event.on_cue = (potty_status == 'on_cue')
        
        event.recorded_by = request.form.get('recorded_by')
        event.notes = request.form.get('notes', '')
        
        timestamp_str = request.form.get('timestamp')
        if timestamp_str:
            event.timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        return redirect(url_for('tables'))
    
    @app.route('/edit_food_event', methods=['POST'])
    def edit_food_event():
        event_id = request.form.get('event_id')
        event = FoodEvent.query.get_or_404(event_id)
        
        amount = request.form.get('amount')
        event.amount = float(amount) if amount else None
        
        event.food_type = request.form.get('food_type')
        event.recorded_by = request.form.get('recorded_by')
        event.notes = request.form.get('notes', '')
        
        timestamp_str = request.form.get('timestamp')
        if timestamp_str:
            event.timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        return redirect(url_for('tables'))
    
    @app.route('/edit_sleep_event', methods=['POST'])
    def edit_sleep_event():
        event_id = request.form.get('event_id')
        event = SleepEvent.query.get_or_404(event_id)
        
        sleep_time_str = request.form.get('sleep_time')
        if sleep_time_str:
            event.sleep_time = datetime.strptime(sleep_time_str, '%Y-%m-%dT%H:%M')
        else:
            event.sleep_time = None
        
        wake_time_str = request.form.get('wake_time')
        if wake_time_str:
            event.wake_time = datetime.strptime(wake_time_str, '%Y-%m-%dT%H:%M')
        else:
            event.wake_time = None
        
        event.recorded_by = request.form.get('recorded_by')
        event.notes = request.form.get('notes', '')
        
        db.session.commit()
        return redirect(url_for('tables'))
    
    @app.route('/edit_walk_event', methods=['POST'])
    def edit_walk_event():
        event_id = request.form.get('event_id')
        event = WalkEvent.query.get_or_404(event_id)
        
        start_time_str = request.form.get('start_time')
        if start_time_str:
            event.start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        
        end_time_str = request.form.get('end_time')
        if end_time_str:
            event.end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            # Calculate duration in minutes
            if event.start_time and event.end_time:
                event.duration = int((event.end_time - event.start_time).total_seconds() / 60)
        else:
            event.end_time = None
            event.duration = None
        
        event.recorded_by = request.form.get('recorded_by')
        event.notes = request.form.get('notes', '')
        
        db.session.commit()
        return redirect(url_for('tables'))
    
    @app.route('/delete_event', methods=['POST'])
    def delete_event():
        event_id = request.form.get('event_id')
        event_type = request.form.get('event_type')
        
        if event_type == 'potty':
            event = PottyEvent.query.get_or_404(event_id)
        elif event_type == 'food':
            event = FoodEvent.query.get_or_404(event_id)
        elif event_type == 'sleep':
            event = SleepEvent.query.get_or_404(event_id)
        elif event_type == 'walk':
            event = WalkEvent.query.get_or_404(event_id)
        else:
            return redirect(url_for('tables'))
        
        db.session.delete(event)
        db.session.commit()
        
        return redirect(url_for('tables'))