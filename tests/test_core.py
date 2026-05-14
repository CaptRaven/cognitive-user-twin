import pytest
from datetime import datetime, timedelta
from core.engine import CognitiveEngine
from core.models import EpisodicMemory
from tests.test_scenarios import (
    create_value_hunter,
    create_quality_seeker,
    create_budget_item,
    create_premium_item,
    create_morning_context
)

def test_engine_basic_evaluation():
    engine = CognitiveEngine()
    user = create_quality_seeker()
    item = create_premium_item()
    context = create_morning_context()
    
    decision = engine.evaluate(user, item, context)
    assert 0 <= decision.score <= 1
    assert decision.label in ["buy", "consider", "skip"]
    assert len(decision.reasoning) > 0

def test_state_update_and_semantic_memory():
    engine = CognitiveEngine()
    user = create_value_hunter()
    item = create_budget_item()
    
    initial_trust = user.trust
    engine.update_state(user, item, 1.0) # Perfect satisfaction
    
    # Trust should increase
    assert user.trust > initial_trust
    # Episodic memory should be added
    assert len(user.memory.episodic) == 1
    assert user.memory.episodic[0].sentiment == 1.0
    
    # Semantic memory for brand should be created/updated
    brand_key = f"brand:{item.brand}"
    assert brand_key in user.memory.semantic
    assert user.memory.semantic[brand_key].strength > user.brand_loyalty

def test_negativity_bias():
    engine = CognitiveEngine()
    user = create_quality_seeker()
    item = create_premium_item()
    
    # Positive experience
    user.trust = 0.5
    engine.update_state(user, item, 0.8)
    pos_drift = user.trust - 0.5
    
    # Negative experience
    user.trust = 0.5
    engine.update_state(user, item, 0.2)
    neg_drift = 0.5 - user.trust
    
    # Negativity bias: trust should drop more for a bad experience than it rises for a good one
    assert neg_drift > pos_drift

def test_memory_decay():
    engine = CognitiveEngine()
    user = create_quality_seeker()
    item = create_premium_item()
    context = create_morning_context()
    
    # 1. Recent bad memory
    bad_memory = EpisodicMemory(item_id="bad", sentiment=-1.0, importance=1.0, timestamp=datetime.now())
    user.memory.episodic.append(bad_memory)
    d_recent = engine.evaluate(user, item, context)
    
    # 2. Old bad memory (decayed)
    user.memory.episodic = []
    old_bad_memory = EpisodicMemory(
        item_id="bad", 
        sentiment=-1.0, 
        importance=1.0, 
        timestamp=datetime.now() - timedelta(days=100)
    )
    user.memory.episodic.append(old_bad_memory)
    d_old = engine.evaluate(user, item, context)
    
    # Score with old bad memory should be higher (less negative influence) than with recent bad memory
    assert d_old.score > d_recent.score
