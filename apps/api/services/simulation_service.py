import logging
from typing import Dict, List, Any, Optional
from core.yelp.models import BehavioralProfile, BehavioralFeatures, UserInteraction
from core.simulation.autonomous_loop import AutonomousLoop
from core.simulation.environment import Environment, EventGenerator
from core.simulation.state_updater import StateUpdater, TimelineManager
from core.recommendation.recommendation_pipeline import RecommendationPipeline
from core.review_generation.review_pipeline import ReviewGenerationPipeline
from core.engine import CognitiveEngine
from apps.api.config import settings

logger = logging.getLogger(__name__)

class SimulationService:
    """
    Manages the singleton state of the autonomous twin for the demo.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimulationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.user_profile: Optional[BehavioralProfile] = None
        self.environment = Environment()
        self.event_generator = EventGenerator()
        self.state_updater = StateUpdater()
        self.timeline = TimelineManager()
        
        # Pipelines
        self.rec_pipeline = RecommendationPipeline()
        self.review_pipeline = ReviewGenerationPipeline(mistral_api_key=settings.MISTRAL_API_KEY)
        self.cognitive_engine = CognitiveEngine()
        
        self.loop: Optional[AutonomousLoop] = None
        self._initialized = True

    def initialize_twin(self, user_id: str = "demo_user_123"):
        """Initializes a new autonomous twin with default features."""
        logger.info(f"Initializing twin: {user_id}")
        features = BehavioralFeatures(
            rating_harshness=0.4,
            exploration_tendency=0.6,
            loyalty_score=0.3,
            emotionality=0.5,
            price_sensitivity=0.4,
            temporal_consistency=0.8
        )
        self.user_profile = BehavioralProfile(
            user_id=user_id,
            features=features,
            history=[],
            metadata={"name": "Demo User", "archetype": "Adventurous Foodie"}
        )
        
        self.loop = AutonomousLoop(
            self.user_profile,
            self.rec_pipeline,
            self.review_pipeline,
            self.cognitive_engine
        )
        # Reset timeline for new twin
        self.timeline = TimelineManager()
        # Reset environment
        self.environment = Environment()
        
        return self.user_profile

    async def step(self) -> List[Dict[str, Any]]:
        """Advances the simulation by 1 hour."""
        if not self.user_profile or not self.loop:
            self.initialize_twin()
            
        # These checks are for the type checker
        if self.user_profile is None or self.loop is None:
            return []

        # 1. Advance Environment
        self.environment.step(minutes=60)
        context = self.environment.get_context()
        
        # 2. Update agent mood/fatigue for time passage
        self.state_updater.process_time_decay(self.user_profile, hours_passed=1)
        
        # 3. Generate events
        events = self.event_generator.generate_events(context)
        step_results = []
        
        for event in events:
            logger.info(f"Processing event: {event['type']}")
            outcome = await self.loop._process_event(event, context)
            
            if outcome:
                # Record in timeline
                self.timeline.record_step(
                    self.environment.current_time,
                    context,
                    self.user_profile,
                    event,
                    outcome
                )
                
                # Update state
                is_review = hasattr(outcome, "rating") or (isinstance(outcome, dict) and "rating" in outcome)
                if is_review:
                    self.state_updater.update_agent_state(self.user_profile, outcome)
                
                step_results.append({
                    "event": event,
                    "outcome": outcome if isinstance(outcome, dict) else outcome.model_dump()
                })
        
        return step_results

    def get_state(self) -> Dict[str, Any]:
        """Returns the current state of the twin and environment."""
        if not self.user_profile:
            return {"status": "not_initialized"}
            
        return {
            "user_id": self.user_profile.user_id,
            "features": self.user_profile.features.model_dump(),
            "metadata": self.user_profile.metadata,
            "environment": {
                "time": str(self.environment.current_time),
                "weather": self.environment.weather,
                "economic_stress": self.environment.economic_stress
            }
        }

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Returns the full behavioral timeline."""
        return self.timeline.history

    def get_analytics(self) -> Dict[str, Any]:
        """Computes detailed behavioral analytics from the timeline."""
        history = self.timeline.history
        if not history:
            return {"status": "no_data"}
            
        # 1. Trajectory Data
        loyalty_trend = [h["user_features"]["loyalty_score"] for h in history]
        exploration_trend = [h["user_features"]["exploration_tendency"] for h in history]
        emotional_trend = [h["user_features"]["emotionality"] for h in history]
        consistency_trend = [h["user_features"]["temporal_consistency"] for h in history]
        
        # 2. Event Analysis
        event_counts = {}
        for h in history:
            etype = h["event"]["type"]
            event_counts[etype] = event_counts.get(etype, 0) + 1
            
        # 3. Decision Satisfaction (if any)
        satisfaction_scores = [
            h["outcome"]["rating"] for h in history 
            if isinstance(h["outcome"], dict) and "rating" in h["outcome"]
        ]
        
        # 4. Behavioral Drift Calculation
        # Difference between first and last states
        if len(history) > 1:
            start_f = history[0]["user_features"]
            end_f = history[-1]["user_features"]
            drift = {k: end_f[k] - start_f[k] for k in start_f.keys() if isinstance(start_f[k], (int, float))}
        else:
            drift = {}

        return {
            "summary": {
                "total_steps": len(history),
                "active_duration_hours": len(history),
                "events_processed": sum(event_counts.values())
            },
            "trends": {
                "loyalty": loyalty_trend,
                "exploration": exploration_trend,
                "emotionality": emotional_trend,
                "consistency": consistency_trend
            },
            "metrics": {
                "avg_satisfaction": sum(satisfaction_scores)/len(satisfaction_scores) if satisfaction_scores else 0,
                "trust_drift": drift.get("loyalty_score", 0),
                "exploration_adaptation": drift.get("exploration_tendency", 0),
                "fatigue_impact": drift.get("temporal_consistency", 0)
            },
            "distribution": {
                "event_types": event_counts
            }
        }
