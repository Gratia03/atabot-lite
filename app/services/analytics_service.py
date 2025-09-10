from datetime import datetime
from typing import Dict, List
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.message_count = 0
        self.session_count = 0
        self.daily_stats = defaultdict(int)
        self.popular_queries = Counter()
        self.response_times = []
        self.error_count = 0
        self.user_feedback = []
    
    async def track_message(self, session_id: str, message: str, response_time: float):
        """Track message analytics"""
        self.message_count += 1
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_stats[today] += 1
        
        # Track popular keywords
        keywords = self._extract_keywords(message.lower())
        self.popular_queries.update(keywords)
        
        # Track response time
        self.response_times.append(response_time)
        if len(self.response_times) > 1000:  # Keep last 1000
            self.response_times = self.response_times[-1000:]
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract meaningful keywords from message"""
        # Remove common words
        stop_words = {'apa', 'bagaimana', 'dimana', 'kapan', 'siapa', 'kenapa', 
                      'adalah', 'dan', 'atau', 'dengan', 'untuk', 'dari', 'ke',
                      'what', 'how', 'where', 'when', 'who', 'why', 'is', 'are'}
        
        words = message.split()
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:5]  # Top 5 keywords
    
    async def track_session_created(self):
        """Track new session creation"""
        self.session_count += 1
    
    async def track_error(self, error_type: str, error_msg: str):
        """Track errors"""
        self.error_count += 1
        logger.error(f"Analytics tracked error: {error_type} - {error_msg}")
    
    async def add_user_feedback(self, session_id: str, rating: int, feedback: str = ""):
        """Add user feedback"""
        self.user_feedback.append({
            "session_id": session_id,
            "rating": rating,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 1000 feedback entries
        if len(self.user_feedback) > 1000:
            self.user_feedback = self.user_feedback[-1000:]
    
    def get_stats(self) -> Dict:
        """Get analytics summary"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "total_messages": self.message_count,
            "total_sessions": self.session_count,
            "daily_stats": dict(self.daily_stats),
            "popular_queries": dict(self.popular_queries.most_common(10)),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "error_count": self.error_count,
            "user_satisfaction": self._calculate_satisfaction(),
            "uptime": "99.9%"  # Placeholder - implement real uptime tracking
        }
    
    def _calculate_satisfaction(self) -> float:
        """Calculate average user satisfaction from feedback"""
        if not self.user_feedback:
            return 0.0
        
        total_rating = sum(feedback["rating"] for feedback in self.user_feedback)
        return round(total_rating / len(self.user_feedback), 2)

# Singleton instance
analytics_service = AnalyticsService()
