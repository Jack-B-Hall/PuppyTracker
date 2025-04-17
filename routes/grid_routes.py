from flask import render_template, request, send_file
from models import PottyEvent, FoodEvent, SleepEvent, WalkEvent
from utils.time_utils import get_local_time
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta

def register_grid_routes(app, db):
    """Register grid view and export routes with the application."""
    
    @app.route('/grid')
    def grid():
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
        
        # Calculate date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Convert dates to datetime for filtering
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Query events
        potty_events = PottyEvent.query.filter(
            PottyEvent.timestamp >= start_datetime,
            PottyEvent.timestamp <= end_datetime
        ).order_by(PottyEvent.timestamp).all()
        
        # Create grid data
        grid_data = {}
        for date in date_range:
            grid_data[date] = {h: [] for h in range(6, 23)}  # 6am to 10pm
        
        # Fill in grid data with potty events
        for event in potty_events:
            event_date = event.timestamp.date()
            event_hour = event.timestamp.hour
            if event_date in grid_data and 6 <= event_hour <= 22:
                event_code = 'U' if event.event_type == 'U' else 'D'
                if event.is_accident:
                    event_code += 'A'
                if event.on_cue:
                    event_code += 'C'
                grid_data[event_date][event_hour].append(event_code)

        # Add Food events to grid
        food_events = FoodEvent.query.filter(
            FoodEvent.timestamp >= start_datetime,
            FoodEvent.timestamp <= end_datetime
        ).order_by(FoodEvent.timestamp).all()
        for event in food_events:
            event_date = event.timestamp.date()
            event_hour = event.timestamp.hour
            if event_date in grid_data and 6 <= event_hour <= 22:
                grid_data[event_date][event_hour].append('F')

        # Add Sleep events to grid
        sleep_events = SleepEvent.query.all()
        for event in sleep_events:
            if not event.sleep_time:
                continue
            start_time = event.sleep_time
            end_time = event.wake_time or event.sleep_time
            if end_time < start_datetime or start_time > end_datetime:
                continue
            current_start = max(start_time, start_datetime)
            current_end = min(end_time, end_datetime)
            for date in date_range:
                for hour in range(6, 23):
                    slot_start = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
                    slot_end = slot_start + timedelta(hours=1)
                    if current_start < slot_end and current_end > slot_start:
                        grid_data[date][hour].append('S')

        # Add Walk events to grid
        walk_events = WalkEvent.query.all()
        for event in walk_events:
            start_time = event.start_time
            end_time = event.end_time or event.start_time
            if end_time < start_datetime or start_time > end_datetime:
                continue
            current_start = max(start_time, start_datetime)
            current_end = min(end_time, end_datetime)
            for date in date_range:
                for hour in range(6, 23):
                    slot_start = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
                    slot_end = slot_start + timedelta(hours=1)
                    if current_start < slot_end and current_end > slot_start:
                        grid_data[date][hour].append('W')
        
        # Compute total sleep duration per day (minutes)
        sleep_totals = {d: 0 for d in date_range}
        # reuse sleep_events from earlier block
        for event in SleepEvent.query.all():
            if not event.sleep_time:
                continue
            start_time = event.sleep_time
            end_time = event.wake_time or event.sleep_time
            for d in date_range:
                day_start = datetime.combine(d, datetime.min.time())
                day_end = day_start + timedelta(days=1)
                overlap_start = max(start_time, day_start)
                overlap_end = min(end_time, day_end)
                if overlap_end > overlap_start:
                    mins = int((overlap_end - overlap_start).total_seconds() // 60)
                    sleep_totals[d] += mins
        # Render with sleep totals
        return render_template(
            'grid.html',
            grid_data=grid_data,
            date_range=date_range,
            start_date=start_date,
            end_date=end_date,
            sleep_totals=sleep_totals
        )
    
    @app.route('/export_grid_pdf')
    def export_grid_pdf():
        # Get filter parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Calculate date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Convert dates to datetime for filtering
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Query events
        potty_events = PottyEvent.query.filter(
            PottyEvent.timestamp >= start_datetime,
            PottyEvent.timestamp <= end_datetime
        ).order_by(PottyEvent.timestamp).all()
        
        # Create grid data
        grid_data = {}
        for date in date_range:
            grid_data[date] = {h: [] for h in range(6, 23)}  # 6am to 10pm
        
        # Fill in grid data with potty events
        for event in potty_events:
            event_date = event.timestamp.date()
            event_hour = event.timestamp.hour
            if event_date in grid_data and 6 <= event_hour <= 22:
                event_code = 'U' if event.event_type == 'U' else 'D'
                if event.is_accident:
                    event_code += 'A'
                if event.on_cue:
                    event_code += 'C'
                grid_data[event_date][event_hour].append(event_code)

        # Add Food events to grid
        food_events = FoodEvent.query.filter(
            FoodEvent.timestamp >= start_datetime,
            FoodEvent.timestamp <= end_datetime
        ).order_by(FoodEvent.timestamp).all()
        for event in food_events:
            event_date = event.timestamp.date()
            event_hour = event.timestamp.hour
            if event_date in grid_data and 6 <= event_hour <= 22:
                grid_data[event_date][event_hour].append('F')

        # Add Sleep events to grid
        sleep_events = SleepEvent.query.all()
        for event in sleep_events:
            if not event.sleep_time:
                continue
            start_time = event.sleep_time
            end_time = event.wake_time or event.sleep_time
            if end_time < start_datetime or start_time > end_datetime:
                continue
            current_start = max(start_time, start_datetime)
            current_end = min(end_time, end_datetime)
            for date in date_range:
                for hour in range(6, 23):
                    slot_start = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
                    slot_end = slot_start + timedelta(hours=1)
                    if current_start < slot_end and current_end > slot_start:
                        grid_data[date][hour].append('S')

        # Add Walk events to grid
        walk_events = WalkEvent.query.all()
        for event in walk_events:
            start_time = event.start_time
            end_time = event.end_time or event.start_time
            if end_time < start_datetime or start_time > end_datetime:
                continue
            current_start = max(start_time, start_datetime)
            current_end = min(end_time, end_datetime)
            for date in date_range:
                for hour in range(6, 23):
                    slot_start = datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
                    slot_end = slot_start + timedelta(hours=1)
                    if current_start < slot_end and current_end > slot_start:
                        grid_data[date][hour].append('W')

        # Compute total sleep duration per day (minutes)
        sleep_totals = {d: 0 for d in date_range}
        for event in SleepEvent.query.all():
            if not event.sleep_time:
                continue
            start_time = event.sleep_time
            end_time = event.wake_time or event.sleep_time
            for d in date_range:
                day_start = datetime.combine(d, datetime.min.time())
                day_end = day_start + timedelta(days=1)
                overlap_start = max(start_time, day_start)
                overlap_end = min(end_time, day_end)
                if overlap_end > overlap_start:
                    mins = int((overlap_end - overlap_start).total_seconds() // 60)
                    sleep_totals[d] += mins
        
        # Create PDF
        buffer = io.BytesIO()
        # Use A4 landscape and tighter margins to fit content
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20
        )
        styles = getSampleStyleSheet()
        
        # Build table data
        table_data = []
        
        # Header row
        header_row = ['Date']
        for hour in range(6, 23):
            header_row.append(f"{hour}:00")
        header_row.append('Sleep')
        table_data.append(header_row)
        
        # Data rows
        for date in date_range:
            row = [date.strftime('%d/%m')]
            for hour in range(6, 23):
                cell_content = ', '.join(grid_data[date][hour]) if grid_data[date][hour] else ''
                row.append(cell_content)
            # Append daily sleep duration
            sleep_mins = sleep_totals.get(date, 0)
            h = sleep_mins // 60
            m = sleep_mins % 60
            sleep_str = f"{h}h {m}m" if m else f"{h}h"
            row.append(sleep_str)
            table_data.append(row)
        
        # Create table
        table = Table(table_data)
        
        # Style the table
        style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            # First column background
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Cell alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            # Body font size and padding
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ])
        table.setStyle(style)
        
        # Add legend and title
        elements = []
        title = Paragraph(f"Puppy Schedule Grid ({start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')})", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        elements.append(table)
        elements.append(Spacer(1, 20))
        legend_text = (
            "U = Urination, D = Defecation, A = Accident, C = On Cue, "
            "W = Walk, F = Food, S = Sleep"
        )
        legend = Paragraph(legend_text, styles['Normal'])
        elements.append(legend)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Create response
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"schedule_grid_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )