import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from core.models import Context, TimeOfDay

logger = logging.getLogger(__name__)

class Environment:
    """
    Simulates a dynamic world environment for the Cognitive User Twin.
    Manages time, weather, economic shifts, and infrastructure stress.
    """
    
    def __init__(self, start_time: Optional[datetime] = None):
        self.current_time = start_time or datetime(2026, 5, 13, 8, 0, 0)
        self.economic_stress = 0.3
        self.weather = "sunny"
        self.location = "Lagos"
        self.base_infrastructure_stress = 0.2
        
    def step(self, minutes: int = 60):
        """Advances the world state by a given number of minutes."""
        self.current_time += timedelta(minutes=minutes)
        self._update_stochastic_factors()
        
    def _update_stochastic_factors(self):
        """Simulates random fluctuations in the world."""
        # Economic stress drifts slowly
        self.economic_stress = max(0.0, min(1.0, self.economic_stress + random.uniform(-0.02, 0.02)))
        
        # Weather shifts
        if random.random() < 0.05:
            self.weather = random.choice(["sunny", "rainy", "cloudy", "stormy"])
            
    def get_context(self) -> Context:
        """Translates current environment state into a Cognitive Context."""
        hour = self.current_time.hour
        
        if 5 <= hour < 12:
            tod = TimeOfDay.MORNING
        elif 12 <= hour < 17:
            tod = TimeOfDay.AFTERNOON
        elif 17 <= hour < 22:
            tod = TimeOfDay.EVENING
        else:
            tod = TimeOfDay.NIGHT
            
        # Traffic stress peaks in Lagos mornings/evenings
        traffic_multiplier = 1.0
        if tod in [TimeOfDay.MORNING, TimeOfDay.EVENING]:
            traffic_multiplier = 2.5
        
        infra_stress = max(0.0, min(1.0, self.base_infrastructure_stress * traffic_multiplier + (0.3 if self.weather == "stormy" else 0.0)))
        
        return Context(
            time_of_day=tod,
            is_weekend=self.current_time.weekday() >= 5,
            location_context=self.location,
            infrastructure_stress=infra_stress,
            economic_context=self.economic_stress,
            mood=None, # To be set by the agent state
            recent_negative_interactions=[]
        )

class EventGenerator:
    """
    Generates realistic daily events/opportunities for the agent.
    """
    
    def generate_events(self, context: Context) -> List[Dict[str, Any]]:
        """Determines what happens to the agent in the current context."""
        events = []
        
        # 1. CORE NEEDS: Hunger / Exploration
        # Peak hunger times
        hunger_chance = 0.0
        if context.time_of_day == TimeOfDay.MORNING: hunger_chance = 0.6
        elif context.time_of_day == TimeOfDay.AFTERNOON: hunger_chance = 0.8
        elif context.time_of_day == TimeOfDay.EVENING: hunger_chance = 0.7
        elif context.time_of_day == TimeOfDay.NIGHT: hunger_chance = 0.2

        if random.random() < hunger_chance:
            events.append({
                "type": "hunger",
                "priority": "high",
                "description": f"The twin is feeling hungry during {context.time_of_day.value}."
            })
        
        # Exploration/Boredom
        exploration_chance = 0.1
        if context.is_weekend: exploration_chance = 0.4
        elif context.time_of_day == TimeOfDay.EVENING: exploration_chance = 0.3
        
        if random.random() < exploration_chance:
            events.append({
                "type": "exploration",
                "priority": "medium",
                "description": "Boredom-driven exploration: Seeking something new."
            })

        # 2. EXTERNAL STRESSORS: Traffic / Infrastructure
        if context.infrastructure_stress > 0.5:
            if random.random() < 0.4:
                events.append({
                    "type": "frustration",
                    "priority": "high",
                    "description": "Severe traffic frustration during commute."
                })
        
        # 3. BUDGET PRESSURE (Economic)
        if context.economic_context is not None and context.economic_context > 0.6:
            if random.random() < 0.3:
                events.append({
                    "type": "budget_pressure",
                    "priority": "medium",
                    "description": "Feeling the pinch of inflation; budget pressure increasing."
                })

        # 4. RANDOM MICRO-EVENTS
        # Late delivery / Service issues (stochastic)
        if random.random() < 0.1:
            events.append({
                "type": "bad_service",
                "priority": "medium",
                "description": "Encountered bad customer service or late delivery."
            })
            
        if random.random() < 0.05:
            events.append({
                "type": "excellent_meal",
                "priority": "medium",
                "description": "Had an unexpectedly excellent meal or service."
            })

        return events
