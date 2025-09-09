import httpx
import numpy as np
from typing import List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.api_key = settings.VOYAGE_API_KEY
        self.model = settings.VOYAGE_MODEL
        self.base_url = "https://api.voyageai.com/v1"
        self.use_embeddings = bool(self.api_key)
        
    async def get_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        """Get embeddings from Voyage API"""
        if not self.use_embeddings:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": texts
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embeddings = [item["embedding"] for item in result["data"]]
                    return np.array(embeddings)
                else:
                    logger.error(f"Embedding API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling Embedding API: {str(e)}")
            return None
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings using numpy"""
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        # Implementasi cosine similarity dengan NumPy
        dot_product = np.dot(embedding1, embedding2)
        norm_1 = np.linalg.norm(embedding1)
        norm_2 = np.linalg.norm(embedding2)
        
        # Hindari pembagian dengan nol
        if norm_1 == 0 or norm_2 == 0:
            return 0.0
            
        similarity = dot_product / (norm_1 * norm_2)
        
        return float(similarity)