import logging
from typing import Dict, Any
from core.models import UserProfile

logger = logging.getLogger(__name__)

class ToneMapper:
    """
    Maps behavioral signals and satisfaction into linguistic tone parameters.
    """
    
    def map_tone(self, user: UserProfile, satisfaction_score: float) -> Dict[str, Any]:
        """
        Determines the review's tone, verbosity, and emotional intensity.
        """
        # Base tone from satisfaction
        if satisfaction_score >= 0.8:
            base_tone = "enthusiastic"
        elif satisfaction_score >= 0.6:
            base_tone = "satisfied"
        elif satisfaction_score >= 0.4:
            base_tone = "neutral"
        elif satisfaction_score >= 0.2:
            base_tone = "disappointed"
        else:
            base_tone = "frustrated"

        # Refine with emotionality and archetype
        emotionality = user.mood # Using mood as a proxy for current emotional state
        
        # Verbosity based on archetype and importance (implied by distance from neutral)
        if user.archetype == "quality_seeker":
            verbosity = "detailed"
            style = "sophisticated"
        elif user.archetype == "value_hunter":
            verbosity = "concise"
            style = "practical"
        else:
            verbosity = "moderate"
            style = "conversational"

        # Emotional intensity
        if emotionality > 0.7:
            intensity = "high"
        elif emotionality < 0.3:
            intensity = "low"
        else:
            intensity = "moderate"

        return {
            "base_tone": base_tone,
            "verbosity": verbosity,
            "emotional_intensity": intensity,
            "review_style": style,
            "sentiment_score": satisfaction_score
        }
