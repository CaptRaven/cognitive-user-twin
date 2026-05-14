import random
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from core.models import UserProfile, Item, Context, Decision, EpisodicMemory, SemanticMemory

class CognitiveEngine:
    """
    Lean Behavioral Engine that simulates human-like decision making
    using episodic and semantic memory.
    """
    def __init__(self, noise: float = 0.05):
        self.noise = noise
        self.weights = {
            'preference': 0.35,
            'budget': 0.2,
            'trust': 0.15,
            'novelty': 0.1,
            'memory': 0.2
        }

    def evaluate(self, user: UserProfile, item: Item, context: Context) -> Decision:
        factors = {}
        reasons = []

        # 1. Semantic Preference Match (Long-term traits)
        match_scores = [1.0 - abs(user.preferences.get(k, 0.5) - v) for k, v in item.features.items()]
        factors['preference'] = float(np.mean(match_scores)) if match_scores else 0.5
        
        # 2. Budget Assessment
        comfort_price = 1000 * (1 - user.budget_sensitivity)
        factors['budget'] = max(0, 1 - (item.price / (comfort_price * 2)))
        if item.price > comfort_price * 1.5: reasons.append("Price significantly exceeds comfort zone")

        # 3. Trust & Brand Semantic Memory
        brand_key = f"brand:{item.brand}"
        brand_memory = user.memory.semantic.get(brand_key)
        brand_trust = brand_memory.strength if brand_memory else user.brand_loyalty
        
        social_proof = (item.rating / 5.0) * (min(item.reviews_count / 100, 1.0))
        factors['trust'] = (brand_trust * 0.4 + social_proof * 0.3 + user.trust * 0.3)
        if factors['trust'] > 0.8: reasons.append(f"Strong established trust in {item.brand}")

        # 4. Novelty Alignment
        factors['novelty'] = 1.0 - abs(user.novelty_preference - item.novelty)

        # 5. Episodic Memory Influence (Short-term experiences with decay)
        memory_influence = 0.5
        if user.memory.episodic:
            # Retrieve relevant memories (simplified: last 5 interactions)
            relevant_memories = user.memory.episodic[-5:]
            influences = [m.get_current_influence() for m in relevant_memories]
            # Normalize influence from [-1, 1] range to [0, 1]
            memory_influence = (np.mean(influences) + 1) / 2
            
            if memory_influence > 0.7: reasons.append("Positive recent experiences with similar items")
            elif memory_influence < 0.3: reasons.append("Hesitation due to past negative experiences")
        
        factors['memory'] = float(memory_influence)

        # Final Scoring with Human Noise
        base_score = sum(self.weights[k] * factors[k] for k in self.weights)
        final_score = max(0, min(1, base_score + random.uniform(-self.noise, self.noise)))

        label = "buy" if final_score > 0.75 else "consider" if final_score > 0.45 else "skip"
        
        return Decision(
            score=final_score,
            label=label,
            reasoning=reasons if reasons else ["Standard evaluation based on traits"],
            factors=factors
        )

    def update_state(self, user: UserProfile, item: Item, satisfaction: float):
        """
        Updates the User Twin's internal state following an interaction.
        Simulates learning, trust drift, and memory formation.
        """
        # 1. Episodic Memory Formation
        sentiment = (satisfaction * 2) - 1 # Scale [0,1] to [-1,1]
        importance = 0.9 if abs(sentiment) > 0.6 else 0.5
        
        new_memory = EpisodicMemory(
            item_id=item.item_id,
            sentiment=sentiment,
            importance=importance,
            timestamp=datetime.now()
        )
        user.memory.episodic.append(new_memory)
        if len(user.memory.episodic) > 20: user.memory.episodic.pop(0)

        # 2. Trust Drift (Negative experiences impact trust more heavily - Negativity Bias)
        learning_rate = 0.15 if satisfaction < 0.4 else 0.05
        user.trust = max(0, min(1, user.trust + (satisfaction - 0.5) * learning_rate))

        # 3. Semantic Memory Evolution (Brand/Category Loyalty)
        brand_key = f"brand:{item.brand}"
        if brand_key not in user.memory.semantic:
            user.memory.semantic[brand_key] = SemanticMemory(concept=brand_key, strength=user.brand_loyalty)
        
        # Gradually update brand trust based on experience
        current_strength = user.memory.semantic[brand_key].strength
        user.memory.semantic[brand_key].strength = max(0, min(1, current_strength + (satisfaction - 0.5) * 0.1))
        user.memory.semantic[brand_key].last_updated = datetime.now()

        # 4. Behavioral Drift
        user.mood = max(0, min(1, user.mood + (satisfaction - 0.5) * 0.2))
        user.fatigue = min(1.0, user.fatigue + 0.05) # Every decision adds slight fatigue
