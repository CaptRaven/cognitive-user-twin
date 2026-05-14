import logging
from typing import List, Dict, Any
from core.yelp.models import BehavioralProfile
from core.models import Context

logger = logging.getLogger(__name__)

class ExplanationGenerator:
    """
    Generates structured reasoning traces for explainable recommendations.
    Transforms component scores into human-readable explanations.
    """

    def generate_explanation(
        self,
        candidate: Dict[str, Any],
        user_profile: BehavioralProfile,
        context: Context
    ) -> Dict[str, Any]:
        """
        Generates a complete explanation trace for a recommendation.
        """
        reasoning = []
        
        reasoning.append(self._explain_primary_factors(candidate, user_profile))
        
        if candidate.get("contextual_adjustments"):
            reasoning.append(self._explain_contextual_effects(candidate, context))
            
        if user_profile.history:
            reasoning.append(self._explain_memory_influence(candidate, user_profile))
            
        reasoning.append(self._explain_archetype_behavior(candidate, user_profile))
        
        return {
            "reasoning_trace": reasoning,
            "confidence": self._compute_confidence(candidate),
            "summary": self._generate_summary(candidate, user_profile)
        }

    def _explain_primary_factors(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> str:
        """Explains the top behavioral factors influencing the recommendation."""
        components = candidate.get("components", {})
        
        sorted_factors = sorted(components.items(), key=lambda x: x[1], reverse=True)
        top_factor = sorted_factors[0]
        
        explanations = {
            "budget_fit": f"matches your price sensitivity (score: {top_factor[1]})",
            "trust_alignment": f"aligns with your trust requirements (score: {top_factor[1]})",
            "novelty_match": f"fits your exploration preference (score: {top_factor[1]})",
            "loyalty_boost": f"matches your brand loyalty pattern (score: {top_factor[1]})",
            "emotional_state": f"aligns with your current mood (score: {top_factor[1]})",
            "memory_influence": f"matches positive past experiences (score: {top_factor[1]})",
            "contextual_relevance": f"fits your current context (score: {top_factor[1]})"
        }
        
        return f"Primary factor: {top_factor[0]} - {explanations.get(top_factor[0], 'relevant match')}"

    def _explain_contextual_effects(self, candidate: Dict[str, Any], context: Context) -> str:
        """Explains how real-time context affected the ranking."""
        adjustments = candidate.get("contextual_adjustments", {})
        effects = []
        
        for name, value in adjustments.items():
            if value > 1.1:
                effects.append(f"{name.replace('_', ' ').title()} boosted score by {((value-1)*100):.0f}%")
            elif value < 0.9:
                effects.append(f"{name.replace('_', ' ').title()} reduced score by {((1-value)*100):.0f}%")
                
        if effects:
            return f"Contextual effects: {', '.join(effects)}"
        return "Context had minimal effect on this recommendation"

    def _explain_memory_influence(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> str:
        """Explains how past experiences influenced this recommendation."""
        memory_score = candidate.get("components", {}).get("memory_influence", 0.5)
        
        if memory_score > 0.7:
            return "Your recent positive experiences significantly boosted this recommendation"
        elif memory_score < 0.4:
            return "Despite limited past data, this recommendation was generated based on other factors"
        else:
            return "Past experiences provided moderate influence on this recommendation"

    def _explain_archetype_behavior(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> str:
        """Explains recommendation in terms of the user's behavioral archetype."""
        archetype = getattr(user_profile.features, 'rating_harshness', 0.5)
        
        if archetype < 0.3:
            return "As a lenient reviewer, you tend to appreciate good service"
        elif archetype > 0.6:
            return "As a critical reviewer, you value quality and consistency"
        else:
            return "You balance quality with value in your decisions"

    def _compute_confidence(self, candidate: Dict[str, Any]) -> float:
        """Computes confidence level in the recommendation."""
        components = candidate.get("components", {})
        
        variance = sum((v - 0.5) ** 2 for v in components.values()) / len(components)
        avg_score = sum(components.values()) / len(components)
        
        if variance < 0.05:
            return 0.9
        elif avg_score > 0.7 or avg_score < 0.3:
            return 0.8
        return 0.6

    def _generate_summary(self, candidate: Dict[str, Any], user_profile: BehavioralProfile) -> str:
        """Generates a one-sentence summary of the recommendation."""
        score = candidate.get("composite_score", 0.5)
        name = candidate.get("metadata", {}).get("name", "this business")
        
        if score > 0.75:
            return f"Highly recommended for you: {name}"
        elif score > 0.55:
            return f"Consider this option: {name}"
        elif score > 0.4:
            return f"You might enjoy: {name}, but don't have strong evidence"
        else:
            return f"Alternative option: {name}, but low alignment with your profile"
