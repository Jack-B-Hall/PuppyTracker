from flask import render_template, request, send_file
from models import PottyEvent
from utils.time_utils import get_local_time
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
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
        
        # Fill in grid data
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
        
        return render_template(
            'grid.html',
            grid_data=grid_data,
            date_range=date_range,
            start_date=start_date,
            end_date=end_date
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
        
        # Fill in grid data
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
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        
        # Build table data
        table_data = []
        
        # Header row
        header_row = ['Date']
        for hour in range(6, 23):
            header_row.append(f"{hour}:00")
        table_data.append(header_row)
        
        # Data rows
        for date in date_range:
            row = [date.strftime('%d/%m')]
            for hour in range(6, 23):
                cell_content = ', '.join(grid_data[date][hour]) if grid_data[date][hour] else ''
                row.append(cell_content)
            table_data.append(row)
        
        # Create table
        table = Table(table_data)
        
        # Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ])
        table.setStyle(style)
        
        # Add legend
        elements = []
        title = Paragraph(f"Potty Schedule Grid ({start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')})", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        elements.append(table)
        elements.append(Spacer(1, 20))
        legend = Paragraph("U = Urination, D = Defecation, A = Accident, C = On Cue", styles['Normal'])
        elements.append(legend)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Create response
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"potty_schedule_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )