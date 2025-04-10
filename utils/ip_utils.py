from flask import request

def get_client_ip():
    """Get the client's real IP address, considering various proxy headers."""
    # Check for X-Forwarded-For header (common with reverse proxies)
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # The first address in the X-Forwarded-For header is the client's real IP
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Check other common proxy headers
    proxy_headers = [
        'X-Real-IP',
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_FORWARDED',
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED_FOR',
        'HTTP_FORWARDED',
        'HTTP_CLIENT_IP'
    ]
    
    for header in proxy_headers:
        value = request.headers.get(header)
        if value:
            return value
    
    # Fall back to remote_addr
    return request.remote_addr

def configure_ip_detection(app):
    """Configure IP detection and logging for the application."""
    if app.debug:
        @app.before_request
        def log_request_info():
            print('Headers:')
            for header, value in request.headers:
                if 'forward' in header.lower() or 'remote' in header.lower() or 'ip' in header.lower():
                    print(f"  {header}: {value}")
            
            # Log the detected client IP
            print(f"Detected client IP: {get_client_ip()}")