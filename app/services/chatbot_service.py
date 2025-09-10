import json
import uuid
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import logging
import numpy as np

from app.models.chat import ChatMessage, ChatRequest, ChatResponse, BotConfig, CompanyData
from app.services.enhanced_llm_service import EnhancedLLMService
from app.services.enhanced_embedding_service import EnhancedEmbeddingService
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.llm_service = EnhancedLLMService()
        self.embedding_service = EnhancedEmbeddingService()
        self.bot_config: Optional[BotConfig] = None
        self.company_data: Optional[CompanyData] = None
        self.sessions: Dict[str, List[ChatMessage]] = {}
        self.faq_embeddings: Optional[np.ndarray] = None
        
        # Load configuration and data
        self._load_data()
        
    def _load_data(self):
        """Load bot configuration and company data from JSON file"""
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self.bot_config = BotConfig(**data.get("bot_config", {}))
            self.company_data = CompanyData(**data.get("company_data", {}))
            
            logger.info("Data loaded successfully")
            
        except FileNotFoundError:
            logger.error("data.json not found")
            # Use default configurations
            self.bot_config = BotConfig()
            self.company_data = CompanyData(
                company_name="Company",
                description="Welcome to our service",
                services=[],
                faq=[],
                contacts={}
            )
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
    
    def create_session(self, session_id: str) -> str:
        """Create a new session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return session_id
            
    async def initialize_embeddings(self):
        """Initialize FAQ embeddings for similarity search"""
        if not self.embedding_service.use_embeddings or not self.company_data.faq:
            return
            
        faq_texts = [f"{item['question']} {item['answer']}" for item in self.company_data.faq]
        self.faq_embeddings = await self.embedding_service.get_embeddings(faq_texts)
        
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process incoming chat message"""
        # Use provided session_id or generate new one
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create session context
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Add user message to context
        user_message = ChatMessage(role="user", content=request.message)
        self.sessions[session_id].append(user_message)
        
        # Find relevant information
        relevant_info = await self._find_relevant_info(request.message)
        
        # Generate response
        response_text = await self._generate_response(
            request.message,
            relevant_info,
            self.sessions[session_id]
        )
        
        # Add assistant response to context
        assistant_message = ChatMessage(role="assistant", content=response_text)
        self.sessions[session_id].append(assistant_message)
        
        # Maintain context size
        if len(self.sessions[session_id]) > settings.MAX_CONTEXT_LENGTH * 2:
            self.sessions[session_id] = self.sessions[session_id][-settings.MAX_CONTEXT_LENGTH * 2:]
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now()
        )
    
    async def process_message_stream(self, request: ChatRequest) -> AsyncGenerator[Dict[str, Any], None]:
        """Process incoming chat message with streaming response"""
        # Use provided session_id or generate new one
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create session context
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Yield session_id first
        yield {"type": "session", "session_id": session_id}
        
        # Add user message to context
        user_message = ChatMessage(role="user", content=request.message)
        self.sessions[session_id].append(user_message)
        
        # Find relevant information
        relevant_info = await self._find_relevant_info(request.message)
        
        # Build prompt
        prompt = self._build_prompt(request.message, relevant_info)
        
        # Generate response with streaming
        full_response = ""
        async for chunk in self.llm_service.generate_response_stream(
            prompt=prompt,
            context=self.sessions[session_id][:-1],  # Exclude the current message
            temperature=self.bot_config.temperature,
            max_tokens=self.bot_config.max_response_length
        ):
            full_response += chunk
            yield {"type": "content", "content": chunk, "session_id": session_id}
        
        # Add assistant response to context
        assistant_message = ChatMessage(role="assistant", content=full_response)
        self.sessions[session_id].append(assistant_message)
        
        # Maintain context size
        if len(self.sessions[session_id]) > settings.MAX_CONTEXT_LENGTH * 2:
            self.sessions[session_id] = self.sessions[session_id][-settings.MAX_CONTEXT_LENGTH * 2:]
        
        # Yield completion signal
        yield {"type": "done", "done": True, "session_id": session_id}
    
    async def _find_relevant_info(self, query: str) -> Dict[str, Any]:
        """Find relevant information from company data"""
        relevant_info = {
            "company_info": self._extract_company_info(query),
            "services": self._find_relevant_services(query),
            "faq": await self._find_similar_faq(query),
            "contacts": self._should_include_contacts(query)
        }
        
        return relevant_info
    
    def _extract_company_info(self, query: str) -> Optional[str]:
        """Extract relevant company information based on query"""
        query_lower = query.lower()
        
        company_keywords = ["perusahaan", "company", "tentang", "about", "apa itu", "what is"]
        if any(keyword in query_lower for keyword in company_keywords):
            return self.company_data.description
            
        return None
    
    def _find_relevant_services(self, query: str) -> List[Dict]:
        """Find services mentioned in the query"""
        query_lower = query.lower()
        relevant_services = []
        
        for service in self.company_data.services:
            service_name = service.get("name", "").lower()
            service_desc = service.get("description", "").lower()
            
            if service_name in query_lower or any(word in service_desc for word in query_lower.split()):
                relevant_services.append(service)
                
        return relevant_services
    
    async def _find_similar_faq(self, query: str) -> List[Dict]:
        """Find similar FAQ items using embeddings or keyword matching"""
        if self.embedding_service.use_embeddings and self.faq_embeddings is not None:
            # Use embeddings for similarity
            query_embedding = await self.embedding_service.get_embeddings([query])
            if query_embedding is not None:
                similarities = []
                for i, faq_emb in enumerate(self.faq_embeddings):
                    sim = self.embedding_service.calculate_similarity(query_embedding[0], faq_emb)
                    if sim > settings.SIMILARITY_THRESHOLD:
                        similarities.append((i, sim))
                
                # Sort by similarity and get top 3
                similarities.sort(key=lambda x: x[1], reverse=True)
                return [self.company_data.faq[i] for i, _ in similarities[:3]]
        
        # Fallback to keyword matching
        query_lower = query.lower()
        relevant_faq = []
        
        for faq_item in self.company_data.faq:
            question_lower = faq_item["question"].lower()
            if any(word in question_lower for word in query_lower.split()):
                relevant_faq.append(faq_item)
                
        return relevant_faq[:3]
    
    def _should_include_contacts(self, query: str) -> Optional[Dict]:
        """Check if contact information should be included"""
        contact_keywords = ["kontak", "contact", "hubungi", "telp", "phone", "email", "alamat", "address"]
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in contact_keywords):
            return self.company_data.contacts
            
        return None
    
    async def _generate_response(
        self,
        query: str,
        relevant_info: Dict[str, Any],
        context: List[ChatMessage]
    ) -> str:
        """Generate response using LLM with relevant information"""
        # Build prompt
        prompt = self._build_prompt(query, relevant_info)
        
        # Generate response
        response = await self.llm_service.generate_response(
            prompt=prompt,
            context=context[:-1],  # Exclude the current message
            temperature=self.bot_config.temperature,
            max_tokens=self.bot_config.max_response_length
        )
        
        return response
    
    def _build_prompt(self, query: str, relevant_info: Dict[str, Any]) -> str:
        """Build prompt for LLM"""
        prompt_parts = [
            f"You are {self.bot_config.name}, a {self.bot_config.personality} assistant for {self.company_data.company_name}.",
            f"Please respond in {self.bot_config.language}.",
            ""
        ]
        
        # Add rules
        if self.bot_config.rules:
            prompt_parts.append("Follow these rules:")
            for rule in self.bot_config.rules:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")
        
        # Add relevant information
        prompt_parts.append("Here is the relevant information to answer the user's question:")
        
        if relevant_info["company_info"]:
            prompt_parts.append(f"\nCompany Description: {relevant_info['company_info']}")
        
        if relevant_info["services"]:
            prompt_parts.append("\nRelevant Services:")
            for service in relevant_info["services"]:
                prompt_parts.append(f"- {service['name']}: {service['description']}")
                if "features" in service:
                    prompt_parts.append(f"  Features: {', '.join(service['features'])}")
                if "price" in service:
                    prompt_parts.append(f"  Price: {service['price']}")
        
        if relevant_info["faq"]:
            prompt_parts.append("\nRelevant FAQ:")
            for faq in relevant_info["faq"]:
                prompt_parts.append(f"Q: {faq['question']}")
                prompt_parts.append(f"A: {faq['answer']}")
        
        if relevant_info["contacts"]:
            prompt_parts.append("\nContact Information:")
            for key, value in relevant_info["contacts"].items():
                prompt_parts.append(f"- {key}: {value}")
        
        prompt_parts.append(f"\nUser Question: {query}")
        prompt_parts.append("\nPlease provide a helpful and accurate response based on the information provided above.")
        
        return "\n".join(prompt_parts)
    
    def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_session_history(self, session_id: str) -> List[ChatMessage]:
        """Get conversation history for a session"""
        return self.sessions.get(session_id, [])