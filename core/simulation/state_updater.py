import logging
from typing import List, Dict, Any
from core.models import UserProfile, Review
from core.yelp.models import BehavioralProfile

logger = logging.getLogger(__name__)

class StateUpdater:
    """
    Updates the agent's internal behavioral state based on experiences.
    Implements behavioral drift, trust evolution, and fatigue.
    """
    
    def update_agent_state(self, profile: BehavioralProfile, interaction_outcome: Any):
        """
        Updates the BehavioralProfile based on a recent interaction.
        Supports both Review objects and dictionaries.
        """
        # Extract rating safely
        rating = 0
        if hasattr(interaction_outcome, "rating"):
            rating = interaction_outcome.rating
        elif isinstance(interaction_outcome, dict) and "rating" in interaction_outcome:
            rating = interaction_outcome["rating"]
        else:
            return # Not a review outcome

        # 1. Trust & Loyalty Evolution
        if rating >= 4:
            # Loyalty increases slower as it gets higher (diminishing returns)
            loyalty_gain = 0.03 * (1.0 - profile.features.loyalty_score)
            profile.features.loyalty_score = min(1.0, profile.features.loyalty_score + loyalty_gain)
            # Good experience reduces stress/emotionality
            profile.features.emotionality = max(0.2, profile.features.emotionality - 0.05)
        elif rating <= 2:
            # Significant drop for bad experience
            profile.features.loyalty_score = max(0.0, profile.features.loyalty_score - 0.15)
            # Bad experience increases emotionality/stress
            profile.features.emotionality = min(1.0, profile.features.emotionality + 0.2)
            # Trust drift: bad experience increases exploration (looking for alternatives)
            profile.features.exploration_tendency = min(1.0, profile.features.exploration_tendency + 0.1)
            
        # 2. Fatigue accumulation
        fatigue_rate = 0.02 + (0.03 * profile.features.emotionality)
        profile.features.temporal_consistency = max(0.0, profile.features.temporal_consistency - fatigue_rate)
        
        # 3. Exploration Adaptation
        if rating == 5:
            profile.features.exploration_tendency = max(0.1, profile.features.exploration_tendency - 0.05)
        
        # 4. Budget Sensitivity Evolution
        # If the user consistently has bad outcomes at expensive places, sensitivity might increase
        # (Simplified: just a small drift based on rating vs price)
        # This would normally need price data from the interaction
        pass

    def process_time_decay(self, profile: BehavioralProfile, hours_passed: int):
        """Simulates the natural decay of mood and fatigue over time."""
        # Mood/Emotionality tends back toward neutral (0.5)
        drift = 0.02 * hours_passed
        if profile.features.emotionality > 0.5:
            profile.features.emotionality = max(0.5, profile.features.emotionality - drift)
        else:
            profile.features.emotionality = min(0.5, profile.features.emotionality + drift)
            
        # Fatigue (temporal_consistency) recovers with time (sleep/rest)
        # If it's night time (not passed here, but could be), recovery is faster
        recovery_rate = 0.05 * hours_passed
        profile.features.temporal_consistency = min(1.0, profile.features.temporal_consistency + recovery_rate)
        
        # Exploration tendency also drifts back to base level
        if profile.features.exploration_tendency > 0.3: # Assuming 0.3 is a base level
             profile.features.exploration_tendency = max(0.3, profile.features.exploration_tendency - (0.01 * hours_passed))

class TimelineManager:
    """
    Manages the history of agent states and decisions.
    """
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        
    def record_step(self, timestamp: Any, context: Any, user_state: Any, event: Any, outcome: Any):
        """Logs a single step in the simulation."""
        
        # Handle outcome serialization
        if hasattr(outcome, 'model_dump'):
            outcome_data = outcome.model_dump()
        elif isinstance(outcome, dict):
            outcome_data = outcome
        else:
            outcome_data = str(outcome)
            
        self.history.append({
            "timestamp": str(timestamp),
            "context": context.model_dump() if hasattr(context, 'model_dump') else str(context),
            "user_features": user_state.features.model_dump(),
            "event": event,
            "outcome": outcome_data
        })
        
    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of the simulation run."""
        if not self.history:
            return {"status": "empty"}
            
        return {
            "steps": len(self.history),
            "start_time": self.history[0]["timestamp"],
            "end_time": self.history[-1]["timestamp"],
            "final_state": self.history[-1]["user_features"]
        }
