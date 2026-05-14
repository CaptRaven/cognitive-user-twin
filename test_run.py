import sys
import os

# Ensure the local project and virtual environment take precedence
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Check for venv and prioritize its site-packages
# This helps if the user is running with a global python but wants venv packages
for version in ["3.12", "3.11", "3.10", "3.9"]:
    venv_site_packages = os.path.join(project_root, "venv", "lib", f"python{version}", "site-packages")
    if os.path.exists(venv_site_packages):
        if venv_site_packages not in sys.path:
            sys.path.insert(0, venv_site_packages)
        break

from core.engine import CognitiveEngine
from core.recommender import RecommendationEngine
from core.models import Context
from tests.test_scenarios import (
    create_value_hunter,
    create_quality_seeker,
    create_budget_item,
    create_premium_item,
    create_morning_context
)
from core.review_gen import ReviewGenerator
from tests.test_core import (
    test_engine_basic_evaluation,
    test_state_update_and_semantic_memory,
    test_negativity_bias,
    test_memory_decay
)

def test_recommendation_basic():
    engine = CognitiveEngine()
    recommender = RecommendationEngine(engine)
    user = create_quality_seeker()
    candidates = [create_budget_item(), create_premium_item()]
    context = create_morning_context()
    
    response = recommender.recommend(user, candidates, context)
    assert len(response.recommendations) > 0
    assert response.user_id == user.user_id
    # Quality seeker should prefer premium
    assert response.recommendations[0].item.name == "Luxury Headphones"

def test_nigerian_realism_lagos_stress():
    engine = CognitiveEngine()
    recommender = RecommendationEngine(engine)
    user = create_value_hunter()
    
    slow_item = create_budget_item()
    slow_item.delivery_speed = 0.2
    
    fast_item = create_budget_item()
    fast_item.item_id = "fast_1"
    fast_item.delivery_speed = 0.9
    
    candidates = [slow_item, fast_item]
    
    # High stress context
    stress_ctx = Context(location_context="Lagos", infrastructure_stress=0.9)
    
    response = recommender.recommend(user, candidates, stress_ctx)
    # Fast item should be prioritized or have the convenience reasoning
    assert response.recommendations[0].item.item_id == "fast_1"
    assert any("convenience" in r.lower() for r in response.recommendations[0].decision.reasoning)

def test_review_generation_consistency():
    engine = CognitiveEngine()
    review_gen = ReviewGenerator()
    user = create_value_hunter()
    item = create_premium_item()
    ctx = create_morning_context()
    
    decision = engine.evaluate(user, item, ctx)
    review = review_gen.generate(user, item, decision, ctx)
    
    # Rating should be low because value hunter skips premium
    assert review.rating <= 3
    assert review.satisfaction_score == decision.score
    assert "Being honest" in review.text # Value hunter tone

# Global client for tests - will be initialized in run_all_tests if needed
client = None

def test_api_health():
    global client
    if client is None:
        from fastapi.testclient import TestClient
        from apps.api.main import app
        client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_simulate_review():
    global client
    if client is None:
        from fastapi.testclient import TestClient
        from apps.api.main import app
        client = TestClient(app)
    
    user = create_value_hunter()
    item = create_budget_item()
    context = create_morning_context()
    
    payload = {
        "user": user.model_dump(),
        "item": item.model_dump(),
        "context": context.model_dump()
    }
    
    response = client.post("/simulate-review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "rating" in data
    assert data["user_id"] == user.user_id

def run_all_tests():
    print("Running All Cognitive Platform tests (including API)...")
    try:
        # Core tests
        test_engine_basic_evaluation()
        print("✓ test_engine_basic_evaluation passed")
        test_state_update_and_semantic_memory()
        print("✓ test_state_update_and_semantic_memory passed")
        test_negativity_bias()
        print("✓ test_negativity_bias passed")
        test_memory_decay()
        print("✓ test_memory_decay passed")
        
        # Rec tests
        test_recommendation_basic()
        print("✓ test_recommendation_basic passed")
        test_nigerian_realism_lagos_stress()
        print("✓ test_nigerian_realism_lagos_stress passed")

        # Review tests
        test_review_generation_consistency()
        print("✓ test_review_generation_consistency passed")
        
        # API tests
        test_api_health()
        print("✓ API /health passed")
        test_api_simulate_review()
        print("✓ API /simulate-review passed")

        print("\n✨ All tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
