import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class ChromaStore:
    """
    Persistent vector store using ChromaDB for cognitive retrieval.
    Manages collections for users, businesses, and interaction memories.
    """
    
    def __init__(self, persist_directory: str = "data/chroma"):
        logger.info(f"Initializing ChromaStore in: {persist_directory}")
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize collections
        self.business_coll = self.client.get_or_create_collection(
            name="businesses",
            metadata={"hnsw:space": "cosine"}
        )
        self.memory_coll = self.client.get_or_create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"}
        )
        self.user_coll = self.client.get_or_create_collection(
            name="users",
            metadata={"hnsw:space": "cosine"}
        )

    def add_businesses(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Adds business embeddings to the store."""
        self.business_coll.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def add_memories(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Adds interaction memories to the store."""
        self.memory_coll.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def add_users(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Adds user behavioral profiles to the store."""
        self.user_coll.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query_businesses(self, query_embeddings: List[List[float]], n_results: int = 10, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Queries for similar businesses with optional metadata filtering."""
        return self.business_coll.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )

    def query_memories(self, query_embeddings: List[List[float]], n_results: int = 10, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Queries for similar interaction memories."""
        return self.memory_coll.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )

    def query_users(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        """Queries for similar user behavioral profiles."""
        return self.user_coll.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
