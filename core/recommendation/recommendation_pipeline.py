import logging
import os
from typing import List, Dict, Any, Optional
from core.yelp.models import BehavioralProfile
from core.models import Context
from core.retrieval.embedding_service import EmbeddingService
from core.retrieval.chroma_store import ChromaStore
from core.retrieval.candidate_retriever import CandidateRetriever
from core.recommendation.recommendation_orchestrator import RecommendationOrchestrator
from core.recommendation.behavioral_scorer import BehavioralScorer
from core.recommendation.contextual_reranker import ContextualReranker
from core.recommendation.explanation_generator import ExplanationGenerator

logger = logging.getLogger(__name__)

class RecommendationPipeline:
    """
    Main entry point for the recommendation system.
    Provides a simple interface for generating behavioral recommendations.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        chroma_persist_dir: str = "data/chroma",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        if hasattr(self, "_initialized"):
            return
            
        logger.info(f"Initializing RecommendationPipeline with model: {embedding_model}")
        
        self.embedding_service = EmbeddingService(model_name=embedding_model)
        self.chroma_store = ChromaStore(persist_directory=chroma_persist_dir)
        self.candidate_retriever = CandidateRetriever(
            self.embedding_service, 
            self.chroma_store
        )
        self.orchestrator = RecommendationOrchestrator(
            self.embedding_service,
            self.chroma_store,
            self.candidate_retriever
        )
        self.behavioral_scorer = BehavioralScorer()
        self.contextual_reranker = ContextualReranker()
        self.explanation_generator = ExplanationGenerator()
        
        self._initialized = True

    async def recommend(
        self,
        user_profile: BehavioralProfile,
        context: Context,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Main recommendation method.
        """
        return await self.orchestrator.orchestrate_recommendation(
            user_profile, 
            context, 
            top_k
        )

    def score_candidates(
        self,
        candidates: List[Dict[str, Any]],
        user_profile: BehavioralProfile,
        context: Context
    ) -> List[Dict[str, Any]]:
        """
        Direct scoring without retrieval.
        Useful when candidates are already known.
        """
        scored = []
        for cand in candidates:
            scores = self.behavioral_scorer.compute_composite_score(cand, user_profile, context)
            scored.append({**cand, **scores})
        return scored

    def rerank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        context: Context,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Direct reranking without orchestration.
        """
        return self.contextual_reranker.rerank(candidates, context, top_k)

    def explain_recommendation(
        self,
        candidate: Dict[str, Any],
        user_profile: BehavioralProfile,
        context: Context
    ) -> Dict[str, Any]:
        """
        Generate explanation for a specific candidate.
        """
        return self.explanation_generator.generate_explanation(candidate, user_profile, context)
