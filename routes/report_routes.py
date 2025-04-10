from flask import render_template, request
from models import PottyEvent, FoodEvent, SleepEvent, WalkEvent
from utils.time_utils import get_local_time
from utils.plotting import create_potty_charts, create_walk_charts
from datetime import datetime, timedelta

def register_report_routes(app, db):
    """Register report routes with the application."""
    
    @app.route('/report')
    def report():
        # Get filter parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        today = get_local_time().date()
        
        # Default to last 7 days if no dates specified
        if not start_date_str:
            start_date = today - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
        if not end_date_str:
            end_date = today
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Convert dates to datetime for filtering
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Query events
        potty_events = PottyEvent.query.filter(
            PottyEvent.timestamp >= start_datetime,
            PottyEvent.timestamp <= end_datetime
        ).order_by(PottyEvent.timestamp).all()
        
        food_events = FoodEvent.query.filter(
            FoodEvent.timestamp >= start_datetime,
            FoodEvent.timestamp <= end_datetime
        ).order_by(FoodEvent.timestamp).all()
        
        sleep_events = SleepEvent.query.filter(
            ((SleepEvent.sleep_time >= start_datetime) & (SleepEvent.sleep_time <= end_datetime)) |
            ((SleepEvent.wake_time >= start_datetime) & (SleepEvent.wake_time <= end_datetime))
        ).order_by(SleepEvent.sleep_time).all()
        
        walk_events = WalkEvent.query.filter(
            WalkEvent.start_time >= start_datetime,
            WalkEvent.start_time <= end_datetime
        ).order_by(WalkEvent.start_time).all()
        
        # Create plots using utility functions
        potty_plots = create_potty_charts(potty_events)
        walk_plots = create_walk_charts(walk_events)
        
        # Combine all plots
        plots = {**potty_plots, **walk_plots}
        
        # Create combined event data for the unified table
        all_events = []
        
        for event in potty_events:
            all_events.append({
                'type': 'potty',
                'timestamp': event.timestamp,
                'event_type': 'Urination' if event.event_type == 'U' else 'Defecation',
                'is_accident': event.is_accident,
                'on_cue': event.on_cue,
                'recorded_by': event.recorded_by,
                'notes': event.notes,
                'id': event.id,
                'display': f'{"Urination" if event.event_type == "U" else "Defecation"} {"(Accident)" if event.is_accident else ""}{"(On Cue)" if event.on_cue else ""}'
            })
        
        for event in food_events:
            all_events.append({
                'type': 'food',
                'timestamp': event.timestamp,
                'amount': event.amount,
                'food_type': event.food_type,
                'recorded_by': event.recorded_by,
                'notes': event.notes,
                'id': event.id,
                'display': f'Food: {event.amount} cups of {event.food_type}'
            })
        
        for event in sleep_events:
            if event.sleep_time:
                all_events.append({
                    'type': 'sleep',
                    'timestamp': event.sleep_time,
                    'recorded_by': event.recorded_by,
                    'notes': event.notes,
                    'id': event.id,
                    'display': 'Bedtime'
                })
            if event.wake_time:
                all_events.append({
                    'type': 'sleep',
                    'timestamp': event.wake_time,
                    'recorded_by': event.recorded_by,
                    'notes': event.notes,
                    'id': event.id,
                    'display': 'Wake Up'
                })
        
        for event in walk_events:
            all_events.append({
                'type': 'walk',
                'timestamp': event.start_time,
                'recorded_by': event.recorded_by,
                'notes': event.notes,
                'id': event.id,
                'display': f'Walk {"(" + str(event.duration) + " min)" if event.duration else "(in progress)"}'
            })
        
        # Sort all events by timestamp
        all_events = sorted(all_events, key=lambda x: x['timestamp'], reverse=True)
        
        return render_template(
            'report.html',
            plots=plots,
            potty_events=potty_events,
            food_events=food_events,
            sleep_events=sleep_events,
            walk_events=walk_events,
            all_events=all_events,
            start_date=start_date,
            end_date=end_date
        )
    
    @app.route('/tables')
    def tables():
        # Get filter parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        today = get_local_time().date()
        
        # Default to last 7 days if no dates specified
        if not start_date_str:
            start_date = today - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
        if not end_date_str:
            end_date = today
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Convert dates to datetime for filtering
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Query events
        potty_events = PottyEvent.query.filter(
            PottyEvent.timestamp >= start_datetime,
            PottyEvent.timestamp <= end_datetime
        ).order_by(PottyEvent.timestamp).all()
        
        food_events = FoodEvent.query.filter(
            FoodEvent.timestamp >= start_datetime,
            FoodEvent.timestamp <= end_datetime
        ).order_by(FoodEvent.timestamp).all()
        
        sleep_events = SleepEvent.query.filter(
            ((SleepEvent.sleep_time >= start_datetime) & (SleepEvent.sleep_time <= end_datetime)) |
            ((SleepEvent.wake_time >= start_datetime) & (SleepEvent.wake_time <= end_datetime))
        ).order_by(SleepEvent.sleep_time).all()
        
        walk_events = WalkEvent.query.filter(
            WalkEvent.start_time >= start_datetime,
            WalkEvent.start_time <= end_datetime
        ).order_by(WalkEvent.start_time).all()
        
        return render_template(
            'tables.html',
            potty_events=potty_events,
            food_events=food_events,
            sleep_events=sleep_events,
            walk_events=walk_events,
            start_date=start_date,
            end_date=end_date
        )