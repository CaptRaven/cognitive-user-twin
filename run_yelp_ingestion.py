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

import logging
from core.yelp.pipeline import YelpIngestionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def run_sample_ingestion():
    """
    Runs a sample ingestion with small limits to verify the pipeline.
    """
    data_dir = "datasets/raw"
    output_dir = "datasets/processed"
    
    pipeline = YelpIngestionPipeline(data_dir, output_dir)
    
    # Run with small sample to verify logic
    # Sample 10 active users with at least 5 reviews
    try:
        profiles = pipeline.run(sample_size=10, min_reviews=5)
        
        print(f"\nSuccessfully processed {len(profiles)} behavioral profiles.")
        for p in profiles[:3]:
            print(f"\nUser: {p.user_id}")
            print(f"Features: {p.features.model_dump()}")
            print(f"History Length: {len(p.history)}")
            
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    run_sample_ingestion()
