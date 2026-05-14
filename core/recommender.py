import random
from typing import List, Optional
from core.models import UserProfile, Item, Context, RecommendationResponse, RecommendedItem
from core.engine import CognitiveEngine

class RecommendationEngine:
    """
    Cognitive Recommendation Engine.
    Prioritizes behavioral realism and contextual reasoning over pure ML metrics.
    """
    def __init__(self, cognitive_engine: CognitiveEngine):
        self.engine = cognitive_engine

    def recommend(
        self, 
        user: UserProfile, 
        candidates: List[Item], 
        context: Context, 
        top_n: int = 3
    ) -> RecommendationResponse:
        """
        The recommendation pipeline:
        1. Candidate Retrieval (already passed in for this demo)
        2. Cognitive Ranking (using the behavioral engine)
        3. Contextual Reranking (applying 'Nigerian realism' and archetypes)
        4. Explanation Generation
        """
        
        # 1. Scoring each candidate using the Cognitive Engine
        scored_candidates = []
        for item in candidates:
            decision = self.engine.evaluate(user, item, context)
            
            # 2. Contextual Reranking (The 'Nigerian Realism' Layer)
            final_score = decision.score
            
            # Example: High infrastructure stress (traffic/power) makes 'Convenience' a priority
            if context.infrastructure_stress > 0.6:
                # Boost items with high delivery speed if user is in a high-stress location like Lagos
                if item.delivery_speed > 0.7:
                    final_score += 0.1
                    decision.reasoning.append("Prioritized due to high convenience in stressful context")
            
            # Example: Affordability sensitivity in specific locations
            if context.location_context == "Rural" and user.budget_sensitivity > 0.7:
                if item.price < 50: # Low price threshold
                    final_score += 0.15
                    decision.reasoning.append("High affordability match for rural context")

            # Example: Trend-following behavior (Impulsive users)
            if user.archetype == "early_adopter" and item.novelty > 0.8:
                final_score += 0.1
                decision.reasoning.append("Matches your tendency for innovative trends")

            scored_candidates.append(RecommendedItem(
                item=item,
                decision=decision,
                score=min(1.0, final_score),
                explanation=decision.reasoning[0] if decision.reasoning else "Personalized match",
                memory_influence=decision.factors.get('memory', 0.5)
            ))

        # 3. Rank and Filter
        # Sort by final adjusted score
        scored_candidates.sort(key=lambda x: x.score, reverse=True)
        
        # 4. Cold-start strategy: 
        # If user has no memory, ensure we include at least one high-trust popular item
        if not user.memory.episodic and len(scored_candidates) > 0:
            # Check if top item is a 'safe' bet
            if scored_candidates[0].item.rating < 4.0:
                # Find a safer bet in the list
                safer_bets = [c for c in scored_candidates if c.item.rating >= 4.0]
                if safer_bets:
                    # Move top safer bet to position 2 to balance novelty and safety
                    safe_bet = safer_bets[0]
                    scored_candidates.remove(safe_bet)
                    scored_candidates.insert(0, safe_bet)

        return RecommendationResponse(
            user_id=user.user_id,
            recommendations=scored_candidates[:top_n],
            context_snapshot={
                "location": context.location_context,
                "stress": context.infrastructure_stress,
                "time": context.time_of_day.value
            }
        )
