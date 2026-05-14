"""
Simplified Test Scenarios and Fixtures
"""

from core.models import UserProfile, Item, ItemCategory, Context, TimeOfDay

def create_value_hunter() -> UserProfile:
    return UserProfile(
        user_id="user_vh_001",
        archetype="value_hunter",
        preferences={"price": 0.9, "quality": 0.4},
        budget_sensitivity=0.9,
        brand_loyalty=0.2,
        novelty_preference=0.2,
        trust=0.3
    )

def create_quality_seeker() -> UserProfile:
    return UserProfile(
        user_id="user_qs_001",
        archetype="quality_seeker",
        preferences={"price": 0.2, "quality": 0.9},
        budget_sensitivity=0.2,
        brand_loyalty=0.8,
        novelty_preference=0.5,
        trust=0.7
    )

def create_budget_item() -> Item:
    return Item(
        item_id="item_b_001",
        name="Cheap Earbuds",
        category=ItemCategory.ELECTRONICS,
        price=19.99,
        features={"quality": 0.3},
        brand="BudgetCo"
    )

def create_premium_item() -> Item:
    return Item(
        item_id="item_p_001",
        name="Luxury Headphones",
        category=ItemCategory.ELECTRONICS,
        price=499.99,
        features={"quality": 0.95},
        brand="LuxAudio",
        brand_tier=0.9,
        rating=4.8,
        reviews_count=1200
    )

def create_morning_context() -> Context:
    return Context(time_of_day=TimeOfDay.MORNING)
