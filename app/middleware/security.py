from fastapi import Request
from fastapi.responses import Response
import re

SUSPICIOUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'on\w+\s*=',
    r'eval\s*\(',
    r'document\.cookie',
]

async def security_middleware(request: Request, call_next):
    # Check for XSS attempts in query params and body
    if request.query_params:
        query_string = str(request.query_params)
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, query_string, re.IGNORECASE):
                return Response("Suspicious request detected", status_code=400)
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response
