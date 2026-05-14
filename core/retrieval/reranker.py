import logging
from typing import List, Dict, Any
from core.yelp.models import BehavioralProfile
from core.engine import CognitiveEngine
from core.models import UserProfile, Item, Context, ItemCategory

logger = logging.getLogger(__name__)

class BehavioralReranker:
    """
    Reranks candidate results using high-fidelity signals from the 
    CognitiveEngine (trust, budget, novelty, etc.)
    """
    
    def __init__(self, cognitive_engine: CognitiveEngine):
        self.engine = cognitive_engine

    def rerank(
        self, 
        user_profile: BehavioralProfile, 
        candidates: List[Dict[str, Any]], 
        context: Context
    ) -> List[Dict[str, Any]]:
        """
        Applies behavioral scoring to a list of retrieved candidates.
        Converts Chroma candidates to Cognitive Items for evaluation.
        """
        logger.info(f"Reranking {len(candidates)} candidates for user: {user_profile.user_id}")
        
        # 1. Map BehavioralProfile to UserProfile (Cognitive Engine format)
        # Note: In a real system, these would be more tightly integrated
        user = self._map_to_user_profile(user_profile)
        
        scored_results = []
        for cand in candidates:
            # 2. Map Candidate metadata to Item
            item = self._map_to_item(cand)
            
            # 3. Evaluate with Cognitive Engine
            decision = self.engine.evaluate(user, item, context)
            
            # 4. Combine retrieval distance with cognitive score
            # Lower distance is better, higher decision score is better
            retrieval_score = 1.0 - cand.get("distance", 0.5)
            final_score = (retrieval_score * 0.3) + (decision.score * 0.7)
            
            scored_results.append({
                **cand,
                "cognitive_score": decision.score,
                "final_score": final_score,
                "reasoning": decision.reasoning
            })
            
        # 5. Sort by final score
        scored_results.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_results

    def _map_to_user_profile(self, bp: BehavioralProfile) -> UserProfile:
        """Helper to convert Yelp BehavioralProfile to Cognitive UserProfile."""
        return UserProfile(
            user_id=bp.user_id,
            archetype="yelp_user",
            preferences={}, # To be filled by category analysis
            budget_sensitivity=bp.features.price_sensitivity,
            brand_loyalty=bp.features.loyalty_score,
            novelty_preference=bp.features.exploration_tendency,
            mood=0.5,
            trust=0.5,
            fatigue=0.0
        )

    def _map_to_item(self, cand: Dict[str, Any]) -> Item:
        """Helper to convert Chroma metadata to Cognitive Item."""
        meta = cand.get("metadata", {})
        return Item(
            item_id=cand.get("id", "unknown"),
            name=meta.get("name", "Unknown Business"),
            category=ItemCategory.FOOD, # Default for Yelp demo
            price=20.0, # Default
            features={},
            brand=meta.get("name", "Unknown"),
            brand_tier=0.5,
            rating=float(meta.get("stars", 0.0)),
            reviews_count=int(meta.get("review_count", 0)),
            novelty=0.5,
            delivery_speed=0.5
        )
