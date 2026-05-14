import logging
from typing import List, Dict, Any
from core.models import Context

logger = logging.getLogger(__name__)

class ContextualReranker:
    """
    Dynamically adapts recommendation rankings based on real-time contextual signals.
    Implements human-realistic context effects: time-of-day, economic stress, mood, etc.
    """

    def __init__(self):
        self.time_decay_factor = 0.05

    def rerank(
        self, 
        candidates: List[Dict[str, Any]], 
        context: Context,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Applies contextual adaptation to a list of scored candidates.
        Returns top-k reranked results.
        """
        logger.info(f"Reranking {len(candidates)} candidates with context adaptation")
        
        reranked = []
        for cand in candidates:
            adapted = self._apply_contextual_adjustments(cand, context)
            reranked.append(adapted)
            
        reranked.sort(key=lambda x: x.get("contextual_score", 0.5), reverse=True)
        
        return reranked[:top_k]

    def _apply_contextual_adjustments(
        self, 
        candidate: Dict[str, Any], 
        context: Context
    ) -> Dict[str, Any]:
        """
        Applies a series of contextual multipliers to the candidate's score.
        Each adjustment reflects a real psychological phenomenon.
        """
        base_score = candidate.get("composite_score", 0.5)
        adjustments = []
        
        time_adj = self._time_of_day_adjustment(candidate, context)
        adjustments.append(("time_of_day", time_adj))
        
        economic_adj = self._economic_context_adjustment(candidate, context)
        adjustments.append(("economic_context", economic_adj))
        
        stress_adj = self._stress_adjustment(candidate, context)
        adjustments.append(("infrastructure_stress", stress_adj))
        
        mood_adj = self._mood_adjustment(candidate, context)
        adjustments.append(("mood", mood_adj))
        
        recent_exp_adj = self._recent_experience_adjustment(candidate, context)
        adjustments.append(("recent_experiences", recent_exp_adj))
        
        final_contextual_score = base_score
        for adj_name, adj_value in adjustments:
            final_contextual_score *= adj_value
            
        final_contextual_score = max(0.0, min(1.0, final_contextual_score))
        
        return {
            **candidate,
            "contextual_score": round(final_contextual_score, 4),
            "contextual_adjustments": {name: round(val, 4) for name, val in adjustments}
        }

    def _time_of_day_adjustment(self, candidate: Dict[str, Any], context: Context) -> float:
        """
        Implements time-of-day effects on decision making.
        People are more decisive in mornings, more exploratory in evenings.
        """
        if not hasattr(context, "time_of_day") or not context.time_of_day:
            return 1.0
            
        time = context.time_of_day
        category = candidate.get("metadata", {}).get("categories", "")
        price = candidate.get("metadata", {}).get("price", 50.0)
        
        if time in ["morning", "afternoon"]:
            if price < 30:
                return 1.15
            return 1.05
        elif time == "evening":
            if any(food in category.lower() for food in ["dinner", "restaurant", "bar"]):
                return 1.20
            return 1.0
        elif time == "late_night":
            if any(food in category.lower() for food in ["fast food", "delivery", "late night"]):
                return 1.25
            return 0.7
            
        return 1.0

    def _economic_context_adjustment(self, candidate: Dict[str, Any], context: Context) -> float:
        """
        Implements economic stress effects on spending behavior.
        High economic stress increases price sensitivity and reduces impulse decisions.
        """
        if not hasattr(context, "economic_context") or context.economic_context is None:
            return 1.0
            
        stress = context.economic_context
        price = candidate.get("metadata", {}).get("price", 50.0)
        
        if stress > 0.7:
            if price > 100:
                return 0.6
            elif price > 50:
                return 0.85
            return 1.1
        elif stress > 0.4:
            return 1.0
            
        return 1.0

    def _stress_adjustment(self, candidate: Dict[str, Any], context: Context) -> float:
        """
        Implements infrastructure or environmental stress effects.
        High stress environments (Lagos traffic) reduce exploration and increase familiarity-seeking.
        """
        if not hasattr(context, "infrastructure_stress") or context.infrastructure_stress is None:
            return 1.0
            
        stress = context.infrastructure_stress
        
        if stress > 0.6:
            category = candidate.get("metadata", {}).get("categories", "")
            if any(fam in category.lower() for fam in ["fast food", "quick service", "delivery"]):
                return 1.3
            return 0.7
        elif stress > 0.3:
            return 0.9
            
        return 1.0

    def _mood_adjustment(self, candidate: Dict[str, Any], context: Context) -> float:
        """
        Implements mood-based recommendation adaptation.
        Positive moods encourage exploration; negative moods seek comfort.
        """
        if not hasattr(context, "mood") or context.mood is None:
            return 1.0
            
        mood = context.mood
        category = candidate.get("metadata", {}).get("categories", "")
        
        comfort_categories = ["comfort food", "bakery", "dessert", "coffee", "ice cream"]
        is_comfort = any(cat in category.lower() for cat in comfort_categories)
        
        if mood < 0.3:
            if is_comfort:
                return 1.4
            return 0.7
        elif mood > 0.7:
            if not is_comfort:
                return 1.2
            return 0.9
            
        return 1.0

    def _recent_experience_adjustment(self, candidate: Dict[str, Any], context: Context) -> float:
        """
        Implements negativity bias from recent bad experiences.
        A recent negative interaction should reduce similar recommendations.
        """
        if not hasattr(context, "recent_negative_interactions"):
            return 1.0
            
        negative_ids = context.recent_negative_interactions
        if not negative_ids:
            return 1.0
            
        candidate_id = candidate.get("id")
        candidate_category = candidate.get("metadata", {}).get("categories", "").lower()
        
        if candidate_id in negative_ids:
            return 0.3
            
        return 1.0
