import logging
import asyncio
from typing import List, Dict, Any, Optional
from core.yelp.models import BehavioralProfile, UserInteraction
from core.models import UserProfile, Item, Decision, Context, TimeOfDay
from core.engine import CognitiveEngine
from core.recommendation.recommendation_pipeline import RecommendationPipeline
from core.review_generation.review_pipeline import ReviewGenerationPipeline
from .environment import Environment, EventGenerator
from .state_updater import StateUpdater, TimelineManager

logger = logging.getLogger(__name__)

class AutonomousLoop:
    """
    The main agentic loop that drives the twin's behavior over simulated time.
    Integrates retrieval, cognition, and generation in a persistent cycle.
    """
    
    def __init__(
        self,
        user_profile: BehavioralProfile,
        rec_pipeline: RecommendationPipeline,
        review_pipeline: ReviewGenerationPipeline,
        cognitive_engine: CognitiveEngine
    ):
        self.user_profile = user_profile
        self.rec_pipeline = rec_pipeline
        self.review_pipeline = review_pipeline
        self.cognitive_engine = cognitive_engine
        
        self.environment = Environment()
        self.event_generator = EventGenerator()
        self.state_updater = StateUpdater()
        self.timeline = TimelineManager()
        
    async def run_simulation(self, steps: int = 24):
        """
        Runs the simulation for a number of steps (each step = 1 hour).
        """
        logger.info(f"Starting autonomous simulation for user: {self.user_profile.user_id}")
        
        for step_idx in range(steps):
            # 1. Advance Environment
            self.environment.step(minutes=60)
            context = self.environment.get_context()
            
            # 2. Update agent mood/fatigue for time passage
            self.state_updater.process_time_decay(self.user_profile, hours_passed=1)
            
            # 3. Generate events for the current context
            events = self.event_generator.generate_events(context)
            
            for event in events:
                logger.info(f"Processing event: {event['type']} at {self.environment.current_time}")
                
                # 4. Agentic Decision Flow
                outcome = await self._process_event(event, context)
                
                if outcome:
                    # 5. Record experience in history
                    self.timeline.record_step(
                        self.environment.current_time,
                        context,
                        self.user_profile,
                        event,
                        outcome
                    )
                    
                    # 6. Update internal behavioral state (drift)
                    self.state_updater.update_agent_state(self.user_profile, outcome)
                    
            # Small async sleep to prevent blocking
            await asyncio.sleep(0.01)
            
        return self.timeline.get_summary()

    async def _process_event(self, event: Dict[str, Any], context: Context) -> Optional[Any]:
        """Handles a specific event by invoking the cognitive pipeline."""
        
        # 1. Decision-making events (require recommendation)
        if event["type"] in ["hunger", "exploration"]:
            # A. Retrieve Candidates
            rec_result = await self.rec_pipeline.recommend(
                self.user_profile,
                context,
                top_k=5
            )
            
            if not rec_result["recommendations"]:
                logger.warning(f"No recommendations found for {event['type']} event.")
                return None
                
            # B. Decision Making
            # Pick the top recommendation
            top_rec = rec_result["recommendations"][0]
            item = self._map_to_item(top_rec)
            
            # Simulated outcome variability based on event type
            # e.g., if it's "exploration", the user might be more critical or more delighted
            
            decision = Decision(
                score=top_rec["composite_score"],
                label="buy",
                reasoning=top_rec["explanation"]["reasoning_trace"],
                factors=top_rec["components"]
            )
            
            # C. Response Generation
            user_core = self._map_to_user_core(self.user_profile)
            review = await self.review_pipeline.generate_review(
                user_core,
                item,
                decision,
                context
            )
            
            # D. Add to internal memory (Interaction Graph)
            self.user_profile.history.append(UserInteraction(
                business_id=item.item_id,
                stars=review.rating,
                text=review.text,
                timestamp=self.environment.current_time,
                business_info=None
            ))
            
            # E. Enrich review with cognitive traces for the UI
            outcome = review.model_dump()
            outcome["reasoning"] = decision.reasoning
            outcome["factors"] = decision.factors
            
            return outcome
            
        # 2. Emotional/Environmental events (update state directly)
        elif event["type"] in ["frustration", "budget_pressure", "bad_service", "excellent_meal"]:
            # These events don't trigger a purchase but change the twin's state
            if event["type"] == "frustration":
                self.user_profile.features.emotionality = min(1.0, self.user_profile.features.emotionality + 0.15)
                self.user_profile.features.temporal_consistency = max(0.0, self.user_profile.features.temporal_consistency - 0.1)
            elif event["type"] == "budget_pressure":
                self.user_profile.features.price_sensitivity = min(1.0, self.user_profile.features.price_sensitivity + 0.05)
            elif event["type"] == "bad_service":
                self.user_profile.features.loyalty_score = max(0.0, self.user_profile.features.loyalty_score - 0.05)
                self.user_profile.features.emotionality = min(1.0, self.user_profile.features.emotionality + 0.1)
            elif event["type"] == "excellent_meal":
                self.user_profile.features.loyalty_score = min(1.0, self.user_profile.features.loyalty_score + 0.05)
                self.user_profile.features.emotionality = max(0.0, self.user_profile.features.emotionality - 0.1)
            
            # Create a dummy review-like object to record in timeline if needed
            # For now, just return a notification of state change
            return {"event_processed": event["type"], "description": event["description"]}

        return None

    def _map_to_item(self, rec: Dict[str, Any]) -> Item:
        from core.models import ItemCategory
        meta = rec.get("metadata", {})
        return Item(
            item_id=rec.get("id", "unknown"),
            name=meta.get("name", "Unknown"),
            category=ItemCategory.FOOD,
            price=float(meta.get("price", 50.0)),
            features={},
            brand=meta.get("name", "Unknown"),
            rating=float(meta.get("stars", 0.0))
        )

    def _map_to_user_core(self, bp: BehavioralProfile) -> UserProfile:
        return UserProfile(
            user_id=bp.user_id,
            archetype="simulated_twin",
            preferences={},
            budget_sensitivity=bp.features.price_sensitivity,
            brand_loyalty=bp.features.loyalty_score,
            novelty_preference=bp.features.exploration_tendency,
            mood=0.5, # Mood is handled by environment/state_updater separately
            trust=0.5
        )

class SimulationRunner:
    """
    Entry point for running large-scale behavioral simulations.
    """
    
    def __init__(self, rec_pipeline: RecommendationPipeline, review_pipeline: ReviewGenerationPipeline):
        self.rec_pipeline = rec_pipeline
        self.review_pipeline = review_pipeline
        self.cognitive_engine = CognitiveEngine()
        
    async def run_agent_day(self, profile: BehavioralProfile, days: int = 1):
        """Runs a simulation for a specific agent for X days."""
        loop = AutonomousLoop(
            profile,
            self.rec_pipeline,
            self.review_pipeline,
            self.cognitive_engine
        )
        
        return await loop.run_simulation(steps=24 * days)
