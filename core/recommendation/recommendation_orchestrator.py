import logging
from typing import List, Dict, Any
from core.yelp.models import BehavioralProfile
from core.models import Context, Item, ItemCategory
from core.retrieval.candidate_retriever import CandidateRetriever
from core.retrieval.embedding_service import EmbeddingService
from core.retrieval.chroma_store import ChromaStore
from core.recommendation.behavioral_scorer import BehavioralScorer
from core.recommendation.contextual_reranker import ContextualReranker
from core.recommendation.explanation_generator import ExplanationGenerator

logger = logging.getLogger(__name__)

class RecommendationOrchestrator:
    """
    Coordinates the full recommendation pipeline from retrieval to explanation.
    Integrates behavioral scoring, contextual reranking, and explainability.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        chroma_store: ChromaStore,
        candidate_retriever: CandidateRetriever
    ):
        self.embedding_service = embedding_service
        self.chroma_store = chroma_store
        self.candidate_retriever = candidate_retriever
        self.behavioral_scorer = BehavioralScorer()
        self.contextual_reranker = ContextualReranker()
        self.explanation_generator = ExplanationGenerator()

    async def orchestrate_recommendation(
        self,
        user_profile: BehavioralProfile,
        context: Context,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Full orchestration pipeline:
        1. Retrieve candidates from vector store
        2. Apply behavioral scoring
        3. Apply contextual reranking
        4. Generate explanations
        """
        logger.info(f"Orchestrating recommendation for user: {user_profile.user_id}")
        
        candidates = await self.candidate_retriever.retrieve_candidates(
            user_profile, 
            n_results=top_k * 2
        )
        
        scored_candidates = []
        for cand in candidates:
            scores = self.behavioral_scorer.compute_composite_score(cand, user_profile, context)
            scored_candidates.append({**cand, **scores})
            
        reranked = self.contextual_reranker.rerank(scored_candidates, context, top_k)
        
        explanations = []
        for cand in reranked:
            exp = self.explanation_generator.generate_explanation(cand, user_profile, context)
            explanations.append({**cand, "explanation": exp})
            
        return {
            "user_id": user_profile.user_id,
            "recommendations": explanations,
            "context": context.model_dump(),
            "total_candidates_evaluated": len(scored_candidates)
        }
