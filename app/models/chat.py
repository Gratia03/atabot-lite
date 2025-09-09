from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        super().__init__(**data)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime

class BotConfig(BaseModel):
    name: str = "Atabot"
    personality: str = "helpful and friendly"
    language: str = "Indonesian"
    max_response_length: int = 500
    temperature: float = 0.7
    rules: List[str] = []

class CompanyData(BaseModel):
    company_name: str
    description: str
    services: List[Dict[str, Any]]
    faq: List[Dict[str, str]]
    contacts: Dict[str, str]
    additional_info: Dict[str, Any] = {}