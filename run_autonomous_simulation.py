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
import logging
from core.yelp.models import BehavioralProfile, BehavioralFeatures
from core.recommendation.recommendation_pipeline import RecommendationPipeline
from core.review_generation.review_pipeline import ReviewGenerationPipeline
from core.simulation.autonomous_loop import SimulationRunner
from apps.api.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

async def run_behavioral_simulation():
    """
    Demonstrates the autonomous behavioral simulation loop.
    """
    print("🚀 Starting Cognitive User Twin: Autonomous Behavioral Simulation")
    print("================================================================")
    
    # 1. Initialize Pipelines
    # Using mock/test data for the demo
    rec_pipeline = RecommendationPipeline(chroma_persist_dir="data/test_chroma")
    review_pipeline = ReviewGenerationPipeline(mistral_api_key=settings.MISTRAL_API_KEY)
    
    # 2. Create a specific agent profile
    # A "Quality Seeker" with low loyalty and high exploration
    agent_profile = BehavioralProfile(
        user_id="autonomous_twin_001",
        features=BehavioralFeatures(
            rating_harshness=0.2,
            exploration_tendency=0.8,
            loyalty_score=0.2,
            category_diversity=0.5,
            price_sensitivity=0.4,
            emotionality=0.5,
            temporal_consistency=0.9
        ),
        history=[]
    )
    
    # 3. Setup Simulation Runner
    runner = SimulationRunner(rec_pipeline, review_pipeline)
    
    print(f"\nTwin Profile Initialized: {agent_profile.user_id}")
    print(f"Initial Loyalty: {agent_profile.features.loyalty_score}")
    print(f"Initial Exploration: {agent_profile.features.exploration_tendency}")
    
    # 4. Run for 2 simulated days (48 hours)
    print("\n⏳ Running simulation for 48 hours...")
    summary = await runner.run_agent_day(agent_profile, days=2)
    
    # 5. Output Results
    print("\n================================================================")
    print("📊 Simulation Summary")
    if 'steps' in summary:
        print(f"Total Steps with Decisions: {summary['steps']}")
        print(f"Start Time: {summary['start_time']}")
        print(f"End Time: {summary['end_time']}")
        
        print("\n📈 Behavioral Drift Results:")
        final_state = summary['final_state']
        print(f"Final Loyalty: {final_state['loyalty_score']:.4f} (Change: {final_state['loyalty_score'] - 0.2:.4f})")
        print(f"Final Exploration: {final_state['exploration_tendency']:.4f} (Change: {final_state['exploration_tendency'] - 0.8:.4f})")
        print(f"Final Fatigue (Consistency): {final_state['temporal_consistency']:.4f}")
    else:
        print("Simulation complete, but no decision events occurred (likely due to empty vector store).")
        print("Note: Run 'python3 run_yelp_ingestion.py' and ensure 'data/test_chroma' is populated.")
    
    print("\n✨ Simulation Complete. The twin has successfully 'lived' for 2 days.")

if __name__ == "__main__":
    asyncio.run(run_behavioral_simulation())
