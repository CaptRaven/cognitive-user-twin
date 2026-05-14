from typing import Dict, Any
from core.models import UserProfile, Item, Context, Decision

class PromptBuilder:
    """
    Constructs structured prompts for Mistral based on cognitive outcomes.
    """
    
    def build_prompt(
        self,
        user: UserProfile,
        item: Item,
        decision: Decision,
        context: Context,
        tone_metadata: Dict[str, Any]
    ) -> str:
        """
        Builds a detailed prompt for review generation.
        """
        reasoning = "\n".join([f"- {r}" for r in decision.reasoning])
        
        prompt = f"""
You are simulating a Yelp review for a user with the following profile:
- Archetype: {user.archetype}
- Mood: {user.mood:.2f} (0=negative, 1=positive)
- Budget Sensitivity: {user.budget_sensitivity:.2f}
- Novelty Preference: {user.novelty_preference:.2f}

The business being reviewed:
- Name: {item.name}
- Category: {item.category}
- Price: ${item.price}
- Rating: {item.rating} stars

The cognitive engine has determined the following outcome:
- Satisfaction Score: {decision.score:.2f}
- Reasoning:
{reasoning}

Contextual Factors:
- Location: {context.location_context}
- Infrastructure Stress: {context.infrastructure_stress:.2f} (traffic, power, etc.)
- Time: {context.time_of_day}

Review Requirements:
- Tone: {tone_metadata['base_tone']}
- Verbosity: {tone_metadata['verbosity']}
- Style: {tone_metadata['review_style']}
- Emotional Intensity: {tone_metadata['emotional_intensity']}

Instructions:
1. Write a realistic, short-form Yelp-style review.
2. DO NOT hallucinate facts about the business not mentioned above.
3. The review MUST reflect the pre-determined satisfaction score and reasoning.
4. Keep it human-like, including slight conversational nuances.
5. If infrastructure stress is high, mention its impact if relevant to the experience.

Review:
"""
        return prompt.strip()
