import re
from typing import Optional

class InputValidator:
    @staticmethod
    def validate_message(message: str) -> tuple[bool, Optional[str]]:
        # Length check
        if len(message) > 1000:
            return False, "Message too long (max 1000 characters)"
        
        # Check for suspicious content
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Suspicious content detected"
        
        return True, None
    
    @staticmethod
    def sanitize_message(message: str) -> str:
        # Remove potential HTML/JS
        message = re.sub(r'<[^>]+>', '', message)
        # Remove excessive whitespace
        message = re.sub(r'\s+', ' ', message.strip())
        return message