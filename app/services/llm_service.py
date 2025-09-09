import httpx
from typing import List, Dict
import logging

from app.core.config import settings
from app.models.chat import ChatMessage

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.poe_api_key = settings.POE_API_KEY
        self.model = settings.POE_MODEL
        self.base_url = "https://api.poe.com/v1"
        
    async def generate_response(
        self,
        prompt: str,
        context: List[ChatMessage] = [],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate response using POE API"""
        try:
            messages = self._prepare_messages(prompt, context)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.poe_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"LLM API error: {response.status_code} - {response.text}")
                    return "Maaf, terjadi kesalahan dalam memproses permintaan Anda."
                    
        except Exception as e:
            logger.error(f"Error calling LLM API: {str(e)}")
            return "Maaf, terjadi kesalahan sistem. Silakan coba lagi."
    
    def _prepare_messages(self, prompt: str, context: List[ChatMessage]) -> List[Dict]:
        """Prepare messages for API call"""
        messages = []
        
        # Add context if available
        for msg in context[-settings.MAX_CONTEXT_LENGTH:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages