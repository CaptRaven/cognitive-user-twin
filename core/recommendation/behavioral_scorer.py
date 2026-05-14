import logging
from typing import List, Dict, Any
from core.yelp.models import BehavioralProfile
from core.models import Context

logger = logging.getLogger(__name__)

class BehavioralScorer:
    """
    Computes behavioral influence scores for recommendations.
    Transforms high-dimensional user signals into actionable scoring weights.
    """

    def score_budget_fit(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> float:
        """Determines how well a candidate matches the user's price sensitivity."""
        price = candidate.get("metadata", {}).get("price", 50.0)
        sensitivity = user_profile.features.price_sensitivity
        
        if price < 20:
            price_score = 0.8 if sensitivity > 0.6 else 0.3
        elif price < 50:
            price_score = 0.9 if sensitivity > 0.4 else 0.5
        elif price < 100:
            price_score = 0.6 if sensitivity < 0.5 else 0.4
        else:
            price_score = 0.3 if sensitivity > 0.3 else 0.7
            
        return price_score * sensitivity

    def score_trust_alignment(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> float:
        """
        Aligns candidate credibility with user's current trust level.
        New or low-rated businesses get penalized for low-trust users.
        """
        meta = candidate.get("metadata", {})
        stars = meta.get("stars", 3.5)
        reviews_count = meta.get("review_count", 0)
        
        trust_baseline = 0.5
        trust_diff = abs(stars - trust_baseline)
        
        if reviews_count < 10:
            credibility = 0.3
        elif reviews_count < 50:
            credibility = 0.6
        else:
            credibility = 0.9
            
        return credibility * (1.0 - trust_diff)

    def score_novelty_match(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> float:
        """Matches novelty-seeking behavior with candidate's uniqueness."""
        novelty_preference = user_profile.features.exploration_tendency
        category = candidate.get("metadata", {}).get("categories", "")
        
        common_categories = ["pizza", "burgers", "coffee"]
        is_common = any(cat.lower() in category.lower() for cat in common_categories)
        
        if is_common:
            novelty_score = 1.0 - novelty_preference
        else:
            novelty_score = novelty_preference
            
        return novelty_score

    def score_loyalty_boost(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> float:
        """
        Boosts candidates that align with user's historically loyal patterns.
        Users with high loyalty scores prefer returning to known brands.
        """
        loyalty = user_profile.features.loyalty_score
        brand = candidate.get("metadata", {}).get("brand", "")
        
        past_brands = set()
        for interaction in user_profile.history[-10:]:
            if interaction.business_info:
                past_brands.add(interaction.business_info.name)
                
        if brand in past_brands:
            return 0.9 * loyalty
        return 0.3 * (1.0 - loyalty)

    def score_emotional_state(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> float:
        """
        Adapts recommendations based on inferred emotional state.
        Stressed/moody users get慰藉 (comfort) recommendations.
        """
        mood = user_profile.features.emotionality
        category = candidate.get("metadata", {}).get("categories", "")
        
        comfort_foods = ["comfort food", "bakery", "dessert", "coffee"]
        is_comfort = any(cat.lower() in category.lower() for cat in comfort_foods)
        
        if mood < 0.4:
            return 0.8 if is_comfort else 0.4
        elif mood > 0.7:
            return 0.9 if not is_comfort else 0.5
        return 0.6

    def score_memory_influence(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> float:
        """
        Weighs candidates against past positive/negative experiences.
        Recency and sentiment of memory influence the score.
        """
        if not user_profile.history:
            return 0.5
            
        memory_weight = 0.0
        for interaction in user_profile.history[-5:]:
            if candidate.get("id") == interaction.business_id:
                if interaction.stars >= 4:
                    memory_weight += 0.8
                elif interaction.stars <= 2:
                    memory_weight -= 0.5
                    
        return max(0.0, min(1.0, 0.5 + memory_weight))

    def score_contextual_relevance(self, candidate: Dict[str, Any], context: Context) -> float:
        """
        Scores based on real-time contextual factors like time and location.
        """
        time_score = 0.5
        if hasattr(context, "time_of_day"):
            if context.time_of_day in ["morning", "afternoon"]:
                time_score = 0.7
            elif context.time_of_day == "evening":
                time_score = 0.9
            elif context.time_of_day == "late_night":
                time_score = 0.4
                
        location_score = 0.6
        if hasattr(context, "infrastructure_stress"):
            if context.infrastructure_stress > 0.5:
                location_score = 0.4
                
        return (time_score + location_score) / 2.0

    def compute_composite_score(
        self, 
        candidate: Dict[str, Any], 
        user_profile: BehavioralProfile, 
        context: Context
    ) -> Dict[str, Any]:
        """
        Aggregates all behavioral signals into a final recommendation score.
        Returns component scores for explainability.
        """
        budget = self.score_budget_fit(candidate, user_profile)
        trust = self.score_trust_alignment(candidate, user_profile)
        novelty = self.score_novelty_match(candidate, user_profile)
        loyalty = self.score_loyalty_boost(candidate, user_profile)
        emotion = self.score_emotional_state(candidate, user_profile)
        memory = self.score_memory_influence(candidate, user_profile)
        contextual = self.score_contextual_relevance(candidate, context)
        
        weights = {
            "budget": 0.15,
            "trust": 0.20,
            "novelty": 0.10,
            "loyalty": 0.10,
            "emotion": 0.10,
            "memory": 0.20,
            "contextual": 0.15
        }
        
        final_score = (
            budget * weights["budget"] +
            trust * weights["trust"] +
            novelty * weights["novelty"] +
            loyalty * weights["loyalty"] +
            emotion * weights["emotion"] +
            memory * weights["memory"] +
            contextual * weights["contextual"]
        )
        
        final_score = max(0.0, min(1.0, final_score))
        
        return {
            "composite_score": round(final_score, 4),
            "components": {
                "budget_fit": round(budget, 4),
                "trust_alignment": round(trust, 4),
                "novelty_match": round(novelty, 4),
                "loyalty_boost": round(loyalty, 4),
                "emotional_state": round(emotion, 4),
                "memory_influence": round(memory, 4),
                "contextual_relevance": round(contextual, 4)
            }
        }
