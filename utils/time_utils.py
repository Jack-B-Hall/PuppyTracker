import pytz
from datetime import datetime

# Global timezone variable
timezone = None

def configure_timezone(tz_name):
    """Configure the application timezone."""
    global timezone
    timezone = pytz.timezone(tz_name)
    return timezone

def get_local_time():
    """Get the current time in the configured timezone."""
    global timezone
    if timezone is None:
        raise RuntimeError("Timezone not configured. Call configure_timezone first.")
    return datetime.now(timezone).replace(tzinfo=None)