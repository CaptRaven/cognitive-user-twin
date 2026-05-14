import random
from typing import List, Dict, Any
from core.models import UserProfile, Item, Context, Review, Decision

class ReviewGenerator:
    """
    Review Generation Pipeline for Cognitive User Twins.
    Translates pre-computed satisfaction scores into human-like reviews.
    """
    
    def __init__(self, nigerian_realism: bool = True):
        self.nigerian_realism = nigerian_realism

    def generate(
        self, 
        user: UserProfile, 
        item: Item, 
        decision: Decision, 
        context: Context
    ) -> Review:
        """The full review generation pipeline."""
        
        # 1. Rating Prediction (Map 0.0-1.0 satisfaction to 1-5 stars)
        rating = self._predict_rating(decision.score)
        
        # 2. Tone Mapping (Determine style based on archetype and mood)
        tone = self._map_tone(user, decision.score)
        
        # 3. Prompt/Content Construction (Assemble the building blocks)
        content_blocks = self._build_content_blocks(user, item, decision, context)
        
        # 4. Review Synthesis (Combine blocks into a cohesive text)
        review_text = self._synthesize_review(content_blocks, tone)
        
        # 5. Postprocessing
        review_text = self._postprocess(review_text)

        return Review(
            user_id=user.user_id,
            item_id=item.item_id,
            rating=rating,
            text=review_text,
            tone=tone,
            satisfaction_score=decision.score,
            behavioral_factors=decision.reasoning,
            memory_influence=decision.factors.get('memory', 0.5)
        )

    def _predict_rating(self, score: float) -> int:
        """Maps satisfaction score to a 1-5 star rating."""
        if score >= 0.85: return 5
        if score >= 0.65: return 4
        if score >= 0.45: return 3
        if score >= 0.25: return 2
        return 1

    def _map_tone(self, user: UserProfile, score: float) -> str:
        """Determines the writing style/persona."""
        if user.archetype == "value_hunter":
            return "critical_and_practical"
        if user.archetype == "quality_seeker":
            return "sophisticated_and_discerning"
        if user.archetype == "early_adopter":
            return "enthusiastic_and_forward_looking"
        return "neutral"

    def _build_content_blocks(self, user: UserProfile, item: Item, decision: Decision, context: Context) -> Dict[str, List[str]]:
        """Constructs the core messages based on the cognitive outcome."""
        blocks = {"praise": [], "complaints": [], "contextual": [], "memory": []}
        
        # Praise/Complaints based on decision reasoning
        for reason in decision.reasoning:
            if "Strong" in reason or "High" in reason:
                blocks["praise"].append(reason)
            elif "above comfort" in reason or "exceeds" in reason or "Hesitation" in reason:
                blocks["complaints"].append(reason)

        # Contextual realism
        if context.infrastructure_stress > 0.6:
            blocks["contextual"].append(f"delivery speed was critical given the {context.location_context} stress")

        # Memory influence
        if len(user.memory.episodic) > 1:
            brand_memory = user.memory.semantic.get(f"brand:{item.brand}")
            if brand_memory and brand_memory.strength > 0.7:
                blocks["memory"].append(f"usually I trust {item.brand}")

        return blocks

    def _synthesize_review(self, blocks: Dict[str, List[str]], tone: str) -> str:
        """Assembles the review text using templates or simple logic."""
        # Note: In a real system, this could call an LLM with the blocks as context.
        # For this hackathon, we use a robust template-based persona synthesizer.
        
        review_parts = []
        
        # Intro based on tone
        if tone == "critical_and_practical":
            review_parts.append("Being honest about this one.")
        elif tone == "sophisticated_and_discerning":
            review_parts.append("A notable experience with this product.")
        else:
            review_parts.append("My thoughts on this.")

        # Main body
        if blocks["praise"]:
            review_parts.append(f"I liked that {', '.join(blocks['praise']).lower()}.")
        
        if blocks["complaints"]:
            review_parts.append(f"However, {', '.join(blocks['complaints']).lower()}.")
        
        if blocks["memory"]:
            review_parts.append(f"Based on my history, {', '.join(blocks['memory']).lower()}.")

        if self.nigerian_realism:
            # Add a touch of local flavor if requested
            flavor = random.choice([
                "Overall, no stories.",
                "It's decent for the price.",
                "Lagos traffic didn't help, but the delivery was okay.",
                "Make we no lie, it's a good one."
            ])
            review_parts.append(flavor)

        return " ".join(review_parts)

    def _postprocess(self, text: str) -> str:
        """Clean up formatting."""
        return text.replace("  ", " ").strip()
