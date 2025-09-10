import numpy as np
from typing import List, Optional
from app.services.embedding_service import EmbeddingService
from app.services.cache_service import cache_service

class EnhancedEmbeddingService(EmbeddingService):
    def __init__(self):
        super().__init__()
        self.embedding_cache_ttl = 86400  # 24 hours
    
    async def get_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        """Get embeddings with caching"""
        if not self.use_embeddings:
            return None
        
        # Create cache key
        cache_key = cache_service._generate_key("embeddings", texts)
        
        # Try to get from cache
        cached_result = cache_service.get(cache_key)
        if cached_result is not None:
            return np.array(cached_result)
        
        # Get from API
        result = await super().get_embeddings(texts)
        
        # Cache the result
        if result is not None:
            cache_service.set(cache_key, result.tolist(), self.embedding_cache_ttl)
        
        return result
