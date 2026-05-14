import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from core.models import UserProfile, Item, Context, Decision, ItemCategory, TimeOfDay
from core.review_generation.review_pipeline import ReviewGenerationPipeline

@pytest.fixture
def sample_user():
    return UserProfile(
        user_id="user_1",
        archetype="value_hunter",
        preferences={},
        budget_sensitivity=0.8,
        brand_loyalty=0.3,
        novelty_preference=0.5,
        mood=0.7
    )

@pytest.fixture
def sample_item():
    return Item(
        item_id="item_1",
        name="Cheap Burgers",
        category=ItemCategory.FOOD,
        price=10.0,
        features={},
        brand="BurgerJoint",
        rating=4.0
    )

@pytest.fixture
def sample_decision():
    return Decision(
        score=0.8,
        label="buy",
        reasoning=["Good price", "Positive brand sentiment"],
        factors={"price": 0.9, "brand": 0.7}
    )

@pytest.fixture
def sample_context():
    return Context(
        time_of_day=TimeOfDay.EVENING,
        location_context="Lagos",
        infrastructure_stress=0.2
    )

@pytest.mark.asyncio
async def test_review_generation_flow(sample_user, sample_item, sample_decision, sample_context):
    # 1. Setup pipeline
    pipeline = ReviewGenerationPipeline(mistral_api_key="fake_key")
    
    # 2. Mock MistralClient
    pipeline.mistral_client.generate_review = AsyncMock(return_value="This burger was actually pretty good for the price! Definitely worth it.")
    
    # 3. Generate review
    review = await pipeline.generate_review(sample_user, sample_item, sample_decision, sample_context)
    
    # 4. Assertions
    assert review.user_id == sample_user.user_id
    assert review.item_id == sample_item.item_id
    assert review.satisfaction_score == sample_decision.score
    assert "burger" in review.text.lower()
    assert review.rating >= 4 # Based on 0.8 satisfaction
    assert review.tone in ["satisfied", "enthusiastic"]
    
    print("\n✓ Review generation flow verified with mock LLM.")

if __name__ == "__main__":
    asyncio.run(test_review_generation_flow(
        sample_user(), sample_item(), sample_decision(), sample_context()
    ))
