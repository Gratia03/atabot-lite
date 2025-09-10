import time
from typing import List
from app.services.llm_service import LLMService
from app.models.chat import ChatMessage
from app.services.cache_service import cache_service
from app.services.analytics_service import analytics_service

class EnhancedLLMService(LLMService):
    def __init__(self):
        super().__init__()
        self.response_cache_ttl = 1800  # 30 minutes for similar queries
    
    async def generate_response(
        self,
        prompt: str,
        context: List[ChatMessage] = [],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        start_time = time.time()
        
        try:
            # Create cache key (only for deterministic queries)
            if temperature <= 0.1:  # Only cache very deterministic responses
                cache_key = cache_service._generate_key("llm_response", {
                    "prompt": prompt[:500],  # Limit prompt length for key
                    "temperature": temperature,
                    "max_tokens": max_tokens
                })
                
                cached_response = cache_service.get(cache_key)
                if cached_response:
                    response_time = time.time() - start_time
                    await analytics_service.track_message("cached", prompt, response_time)
                    return cached_response
            
            # Generate response
            response = await super().generate_response(prompt, context, temperature, max_tokens)
            
            # Cache deterministic responses
            if temperature <= 0.1 and response:
                cache_service.set(cache_key, response, self.response_cache_ttl)
            
            # Track analytics
            response_time = time.time() - start_time
            await analytics_service.track_message("generated", prompt, response_time)
            
            return response
            
        except Exception as e:
            await analytics_service.track_error("llm_service", str(e))
            raise
