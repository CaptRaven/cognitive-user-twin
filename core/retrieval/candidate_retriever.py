import logging
from typing import List, Dict, Any, Optional
from .embedding_service import EmbeddingService
from .chroma_store import ChromaStore
from core.yelp.models import BehavioralProfile

logger = logging.getLogger(__name__)

class CandidateRetriever:
    """
    Retrieves potential business candidates based on behavioral similarity 
    and contextual relevance.
    """
    
    def __init__(self, embedding_service: EmbeddingService, chroma_store: ChromaStore):
        self.embedding_service = embedding_service
        self.chroma_store = chroma_store

    async def retrieve_candidates(
        self, 
        user_profile: BehavioralProfile, 
        n_results: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves businesses that match the user's behavioral profile.
        Uses user embedding to find semantically similar business contexts.
        """
        logger.info(f"Retrieving candidates for user: {user_profile.user_id}")
        
        # 1. Generate user behavioral embedding
        user_embedding = self.embedding_service.embed_user_behavior(user_profile).tolist()
        
        # 2. Query Chroma for similar businesses
        results = self.chroma_store.query_businesses(
            query_embeddings=[user_embedding],
            n_results=n_results,
            where=filters
        )
        
        # 3. Format results
        candidates = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                candidates.append({
                    "id": results['ids'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        
        return candidates

class MemoryRetriever:
    """
    Retrieves relevant prior experiences (memories) for a user to inform
    current decision-making and review generation.
    """
    
    def __init__(self, embedding_service: EmbeddingService, chroma_store: ChromaStore):
        self.embedding_service = embedding_service
        self.chroma_store = chroma_store

    async def retrieve_relevant_memories(
        self, 
        user_id: str, 
        query_text: str, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves memories (interactions) for a specific user that are
        semantically related to the current query (e.g., "Italian food").
        """
        logger.info(f"Retrieving memories for user {user_id} with query: {query_text}")
        
        # 1. Generate query embedding
        query_embedding = self.embedding_service.embed_text(query_text).tolist()
        
        # 2. Query Chroma for user's memories
        # Filter by user_id to ensure we only get this user's experiences
        results = self.chroma_store.query_memories(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"user_id": user_id}
        )
        
        # 3. Format results
        memories = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                memories.append({
                    "id": results['ids'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        
        return memories
