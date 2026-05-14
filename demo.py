#!/usr/bin/env python3
"""
Cognitive User Twin - Full Pipeline Demo
Evaluates an item -> Updates user state -> Generates a behavioral review.
"""
import sys
sys.path.insert(0, '.')

from core.engine import CognitiveEngine
from core.recommender import RecommendationEngine
from core.review_gen import ReviewGenerator
from core.models import Context
from tests.test_scenarios import (
    create_quality_seeker,
    create_value_hunter,
    create_premium_item,
    create_budget_item
)

def main():
    cog_engine = CognitiveEngine()
    review_gen = ReviewGenerator(nigerian_realism=True)
    
    # 1. Setup User and Item
    vh = create_value_hunter() # High budget sensitivity
    premium = create_premium_item()
    ctx = Context(location_context="Lagos", infrastructure_stress=0.7)

    print("=== STEP 1: COGNITIVE EVALUATION ===")
    decision = cog_engine.evaluate(vh, premium, ctx)
    print(f"Satisfaction Score: {decision.score:.2f}")
    print(f"Decision: {decision.label.upper()}")
    print(f"Factors: {decision.reasoning}")

    print("\n=== STEP 2: STATE UPDATE (Post-Interaction) ===")
    # Simulate the user actually interacting with the item
    # Since satisfaction was likely low (value hunter vs premium), trust might drop
    cog_engine.update_state(vh, premium, decision.score)
    print(f"New User Trust: {vh.trust:.2f}")
    print(f"Episodic Memories: {len(vh.memory.episodic)}")

    print("\n=== STEP 3: BEHAVIORAL REVIEW GENERATION ===")
    # The generator uses the pre-computed satisfaction score and user archetype
    review = review_gen.generate(vh, premium, decision, ctx)
    
    print(f"Rating: {'⭐' * review.rating} ({review.rating}/5)")
    print(f"Tone: {review.tone}")
    print("-" * 40)
    print(f"Review Text: \"{review.text}\"")
    print("-" * 40)

    # Demo 2: Quality Seeker with high trust
    print("\n=== DEMO 2: QUALITY SEEKER (Loyal Persona) ===")
    qs = create_quality_seeker()
    qs_decision = cog_engine.evaluate(qs, premium, ctx)
    # Give them a history of positive interactions
    cog_engine.update_state(qs, premium, 0.9)
    cog_engine.update_state(qs, premium, 0.9)
    
    qs_review = review_gen.generate(qs, premium, qs_decision, ctx)
    print(f"User: {qs.archetype}")
    print(f"Rating: {'⭐' * qs_review.rating}")
    print(f"Review Text: \"{qs_review.text}\"")

if __name__ == "__main__":
    main()
