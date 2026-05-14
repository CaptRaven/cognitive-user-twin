import logging
from typing import Dict, Any
from core.models import UserProfile, Item, Context, Review, Decision
from .tone_mapper import ToneMapper
from .rating_mapper import RatingMapper
from .prompt_builder import PromptBuilder
from .mistral_client import MistralClient
from .review_postprocessor import ReviewPostprocessor

logger = logging.getLogger(__name__)

class ReviewGenerationPipeline:
    """
    Orchestrates the transition from cognitive outcome to natural language review.
    """
    
    def __init__(self, mistral_api_key: str = ""):
        self.tone_mapper = ToneMapper()
        self.rating_mapper = RatingMapper()
        self.prompt_builder = PromptBuilder()
        self.mistral_client = MistralClient(api_key=mistral_api_key if mistral_api_key else None)
        self.postprocessor = ReviewPostprocessor()

    async def generate_review(
        self,
        user: UserProfile,
        item: Item,
        decision: Decision,
        context: Context
    ) -> Review:
        """
        Generates a realistic review based on behavioral and cognitive state.
        """
        logger.info(f"Generating review for user {user.user_id} and item {item.item_id}")
        
        # 1. Determine Tone and Rating
        tone_metadata = self.tone_mapper.map_tone(user, decision.score)
        rating = self.rating_mapper.map_rating(decision.score, user.fatigue) # Using fatigue as proxy for harshness for now
        
        # 2. Build Prompt
        prompt = self.prompt_builder.build_prompt(
            user, item, decision, context, tone_metadata
        )
        
        # 3. Generate Text via Mistral
        raw_text = await self.mistral_client.generate_review(prompt)
        
        # 4. Post-process
        final_text = self.postprocessor.process(raw_text)
        
        return Review(
            user_id=user.user_id,
            item_id=item.item_id,
            rating=rating,
            text=final_text,
            tone=tone_metadata["base_tone"],
            satisfaction_score=decision.score,
            behavioral_factors=decision.reasoning,
            memory_influence=decision.factors.get("memory", 0.5),
            metadata={
                "tone_details": tone_metadata,
                "prompt_used": prompt[:100] + "..." # Log start of prompt for debugging
            }
        )
