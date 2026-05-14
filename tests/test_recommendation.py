import pytest
import asyncio
from core.yelp.models import BehavioralProfile, BehavioralFeatures, UserInteraction
from core.models import Context, TimeOfDay
from core.recommendation.behavioral_scorer import BehavioralScorer
from core.recommendation.contextual_reranker import ContextualReranker
from core.recommendation.explanation_generator import ExplanationGenerator

@pytest.fixture
def sample_user_profile():
    return BehavioralProfile(
        user_id="test_user_123",
        features=BehavioralFeatures(
            rating_harshness=0.3,
            exploration_tendency=0.7,
            loyalty_score=0.4,
            category_diversity=0.6,
            price_sensitivity=0.8
        ),
        history=[]
    )

@pytest.fixture
def sample_candidates():
    return [
        {
            "id": "biz_1",
            "metadata": {
                "name": "Luigi's Italian",
                "categories": "Italian, Restaurant, Dinner",
                "price": 85.0,
                "stars": 4.5,
                "review_count": 150
            },
            "distance": 0.2
        },
        {
            "id": "biz_2",
            "metadata": {
                "name": "Quick Bites",
                "categories": "Fast Food, Quick Service",
                "price": 15.0,
                "stars": 3.8,
                "review_count": 45
            },
            "distance": 0.5
        },
        {
            "id": "biz_3",
            "metadata": {
                "name": "The Luxury Spa",
                "categories": "Spa, Wellness, Beauty",
                "price": 200.0,
                "stars": 4.8,
                "review_count": 300
            },
            "distance": 0.3
        }
    ]

@pytest.fixture
def sample_context():
    return Context(
        time_of_day=TimeOfDay.EVENING,
        is_weekend=True,
        infrastructure_stress=0.2,
        economic_context=0.6,
        mood=0.7
    )

def test_behavioral_scorer(sample_user_profile, sample_candidates, sample_context):
    scorer = BehavioralScorer()
    
    for cand in sample_candidates:
        result = scorer.compute_composite_score(cand, sample_user_profile, sample_context)
        
        assert "composite_score" in result
        assert "components" in result
        assert 0.0 <= result["composite_score"] <= 1.0
        
        print(f"\nCandidate: {cand['metadata']['name']}")
        print(f"Score: {result['composite_score']}")
        print(f"Components: {result['components']}")

def test_contextual_reranker(sample_candidates, sample_context):
    reranker = ContextualReranker()
    
    for cand in sample_candidates:
        cand["composite_score"] = 0.6
        
    reranked = reranker.rerank(sample_candidates, sample_context, top_k=3)
    
    assert len(reranked) == 3
    assert "contextual_score" in reranked[0]
    assert "contextual_adjustments" in reranked[0]
    
    print("\nReranked Results:")
    for cand in reranked:
        print(f"  {cand['metadata']['name']}: {cand['contextual_score']}")

def test_explanation_generator(sample_user_profile, sample_candidates, sample_context):
    scorer = BehavioralScorer()
    generator = ExplanationGenerator()
    
    cand = sample_candidates[0]
    scores = scorer.compute_composite_score(cand, sample_user_profile, sample_context)
    cand_with_scores = {**cand, **scores}
    
    explanation = generator.generate_explanation(cand_with_scores, sample_user_profile, sample_context)
    
    assert "reasoning_trace" in explanation
    assert "confidence" in explanation
    assert "summary" in explanation
    assert len(explanation["reasoning_trace"]) > 0
    
    print("\nExplanation:")
    for reason in explanation["reasoning_trace"]:
        print(f"  - {reason}")
    print(f"Confidence: {explanation['confidence']}")
    print(f"Summary: {explanation['summary']}")

def test_full_pipeline_flow(sample_user_profile, sample_candidates, sample_context):
    scorer = BehavioralScorer()
    reranker = ContextualReranker()
    generator = ExplanationGenerator()
    
    scored = []
    for cand in sample_candidates:
        scores = scorer.compute_composite_score(cand, sample_user_profile, sample_context)
        scored.append({**cand, **scores})
    
    reranked = reranker.rerank(scored, sample_context, top_k=3)
    
    for cand in reranked:
        exp = generator.generate_explanation(cand, sample_user_profile, sample_context)
        cand["explanation"] = exp
    
    print("\n=== Full Pipeline Results ===")
    for i, cand in enumerate(reranked, 1):
        print(f"\n{i}. {cand['metadata']['name']}")
        print(f"   Final Score: {cand['contextual_score']}")
        print(f"   Summary: {cand['explanation']['summary']}")
    
    assert len(reranked) == 3
    assert reranked[0]["contextual_score"] >= reranked[1]["contextual_score"]
    
    print("\n✓ Full recommendation pipeline verified successfully!")

if __name__ == "__main__":
    import os
    os.makedirs("data/test_chroma", exist_ok=True)
    
    test_behavioral_scorer(
        sample_user_profile(), 
        sample_candidates(), 
        sample_context()
    )
    test_contextual_reranker(sample_candidates(), sample_context())
    test_explanation_generator(
        sample_user_profile(), 
        sample_candidates(), 
        sample_context()
    )
    test_full_pipeline_flow(
        sample_user_profile(), 
        sample_candidates(), 
        sample_context()
    )
