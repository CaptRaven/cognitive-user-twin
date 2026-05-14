import sys
import os

# Ensure the local project and virtual environment take precedence
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Check for venv and prioritize its site-packages
for version in ["3.12", "3.11", "3.10", "3.9"]:
    venv_site_packages = os.path.join(project_root, "venv", "lib", f"python{version}", "site-packages")
    if os.path.exists(venv_site_packages):
        if venv_site_packages not in sys.path:
            sys.path.insert(0, venv_site_packages)
        break

import asyncio
from core.models import UserProfile, Item, Context, Decision, ItemCategory, TimeOfDay
from core.review_generation.review_pipeline import ReviewGenerationPipeline
from apps.api.config import settings

async def test_real_generation():
    print("--- Starting Real Mistral Review Generation ---")
    
    # 1. Initialize Pipeline with the key from settings
    pipeline = ReviewGenerationPipeline(mistral_api_key=settings.MISTRAL_API_KEY)
    
    # 2. Define a realistic scenario
    user = UserProfile(
        user_id="user_demo_1",
        archetype="quality_seeker",
        preferences={},
        budget_sensitivity=0.4,
        brand_loyalty=0.8,
        novelty_preference=0.3,
        mood=0.8, # Happy mood
        fatigue=0.1
    )
    
    item = Item(
        item_id="biz_luxury_italy",
        name="La Piazza Gourmet",
        category=ItemCategory.FOOD,
        price=120.0,
        features={},
        brand="La Piazza",
        rating=4.7
    )
    
    decision = Decision(
        score=0.92, # High satisfaction
        label="buy",
        reasoning=[
            "Excellent authentic flavors",
            "High-end ambiance matches quality seeker profile",
            "Consistent with previous positive brand experiences"
        ],
        factors={"quality": 0.95, "ambiance": 0.9, "brand": 0.85}
    )
    
    context = Context(
        time_of_day=TimeOfDay.EVENING,
        location_context="Lagos (Victoria Island)",
        infrastructure_stress=0.1
    )
    
    # 3. Generate
    print(f"Generating review for {item.name}...")
    try:
        review = await pipeline.generate_review(user, item, decision, context)
        
        print("\n--- GENERATED REVIEW ---")
        print(f"Rating: {review.rating} Stars")
        print(f"Tone: {review.tone}")
        print(f"Text: \"{review.text}\"")
        print("-------------------------")
        
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    if not settings.MISTRAL_API_KEY:
        print("MISTRAL_API_KEY is not set. Please check your .env file.")
    else:
        asyncio.run(test_real_generation())
