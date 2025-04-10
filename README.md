# Puppy Tracker

A comprehensive web application for tracking and visualizing your puppy's daily activities, including potty events, meals, walks, and sleep schedule.

## Features

- **Activity Tracking**
  - Potty events (urination, defecation, accidents, and on-cue successes)
  - Feeding (amount, food type)
  - Walking (start/end time, duration)
  - Sleep (bedtime, wake time)

- **Data Visualization**
  - Daily potty event trends with type breakdown
  - Potty training progress (success vs. accident rates)
  - Hourly activity patterns
  - Walking patterns and duration analysis
  - Time intervals between potty events

- **User Conveniences**
  - Multi-user support with different recorders
  - Custom time entry for backdated events
  - Per-device settings and preferences
  - Auto-completion of related events (e.g., automatically creates sleep events)
  - Data export capabilities (PDF potty schedule grid)

- **Data Management**
  - Detailed event tables with filtering options
  - Edit and delete functionality for all events
  - Date range filtering

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Jack-B-Hall/PuppyTracker.git
   cd puppy-tracker

Install dependencies:
pip install -r requirements.txt

Create a .env file in the project root with the following content (update as needed):
# Database configuration
DATABASE_URL=sqlite:///pet_tracker.db

# Application settings
SECRET_KEY=your-secure-secret-key-here

# Server settings
HOST=0.0.0.0
PORT=5000

# Time zone settings
TIME_ZONE=Your/Timezone

# Debug settings (True/False)
DEBUG=True


# Running the Application
# Development Mode
python app.py --port=5000

The application will be accessible at: http://localhost:5000/PuppyTracker

# Production Deployment
For production deployment, it's recommended to use a WSGI server like Gunicorn and a reverse proxy like Nginx:
bashgunicorn -w 4 -b 127.0.0.1:5000 app:app

Example Nginx configuration:
location /PuppyTracker {
    proxy_pass http://localhost:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
# Usage Guide
# Adding Events

From the main page, select the type of event you want to record (potty, food, walk, or sleep).
Fill in the required information.
For potty events, indicate whether it was "On Cue" or an "Accident".
Optionally add notes and select a different recorder.
Use the "Custom Time" option if you need to backdate an event.

# Viewing Reports

Navigate to the Reports page.
Use the date filters to select your date range.
View the visualizations for insights into your puppy's patterns.
Scroll down to see all events in chronological order.
Use the tabs to view specific event types in detail.

# Customizing Preferences

Go to the Preferences page.
Set your default recorder name.
Configure default food amounts and types.
Set walk duration parameters and auto-end thresholds.
Configure sleep schedule defaults.

# License
This project is licensed under the MIT License - see the LICENSE file for details.

# Acknowledgments

Bootstrap 4 for UI components
Plotly for data visualization
Flask for the web framework
SQLAlchemy for database ORM