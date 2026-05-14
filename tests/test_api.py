import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
import json

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data

def test_simulate_review():
    payload = {
        "user": {
            "user_id": "user_123",
            "archetype": "value_hunter",
            "preferences": {"battery": 0.9, "price": 0.8},
            "budget_sensitivity": 0.9,
            "brand_loyalty": 0.3,
            "novelty_preference": 0.2,
            "mood": 0.5,
            "trust": 0.5,
            "fatigue": 0.0,
            "memory": {"episodic": [], "semantic": {}}
        },
        "item": {
            "item_id": "item_456",
            "name": "Cheap Phone",
            "category": "electronics",
            "price": 500.0,
            "features": {"battery": 0.8, "screen": 0.5},
            "brand": "BudgetCo",
            "brand_tier": 0.3,
            "rating": 4.0,
            "reviews_count": 50,
            "novelty": 0.1,
            "delivery_speed": 0.8
        },
        "context": {
            "time_of_day": "morning",
            "is_weekend": False,
            "device": "mobile",
            "time_pressure": 0.1,
            "location_context": "Lagos",
            "infrastructure_stress": 0.3
        }
    }
    response = client.post("/simulate-review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "satisfaction_score" in data
    assert "behavioral_factors" in data

def test_recommend():
    payload = {
        "user": {
            "user_id": "user_123",
            "archetype": "value_hunter",
            "preferences": {"battery": 0.9},
            "budget_sensitivity": 0.9,
            "brand_loyalty": 0.3,
            "novelty_preference": 0.2,
            "memory": {"episodic": [], "semantic": {}}
        },
        "candidates": [
            {
                "item_id": "item_1",
                "name": "Phone A",
                "category": "electronics",
                "price": 400.0,
                "features": {"battery": 0.9},
                "brand": "BrandA"
            },
            {
                "item_id": "item_2",
                "name": "Phone B",
                "category": "electronics",
                "price": 800.0,
                "features": {"battery": 0.7},
                "brand": "BrandB"
            }
        ],
        "context": {
            "time_of_day": "morning",
            "location_context": "Lagos"
        },
        "top_n": 2
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) <= 2
    assert "explanation" in data["recommendations"][0]

def test_user_update():
    payload = {
        "user": {
            "user_id": "user_123",
            "archetype": "value_hunter",
            "preferences": {},
            "budget_sensitivity": 0.5,
            "brand_loyalty": 0.5,
            "novelty_preference": 0.5,
            "memory": {"episodic": [], "semantic": {}}
        },
        "item": {
            "item_id": "item_1",
            "name": "Phone A",
            "category": "electronics",
            "price": 400.0,
            "features": {},
            "brand": "BrandA"
        },
        "satisfaction": 0.8
    }
    response = client.post("/user/update", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "memory" in data
    assert len(data["memory"]["episodic"]) > 0
