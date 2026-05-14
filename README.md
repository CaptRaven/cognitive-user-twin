# Cognitive User Twin Platform

## Production-Grade AI Behavioral Simulation

### Setup & Startup

1. **Local Installation**
   ```bash
   # Create a virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the API
   python apps/api/main.py
   ```

2. **Running Tests**
   ```bash
   # Run all tests including API endpoints
   ./venv/bin/python3 test_run.py
   
   # Or using pytest directly
   ./venv/bin/python3 -m pytest tests/test_api.py
   ```

2. **Docker Setup**
   ```bash
   docker build -t cognitive-user-twin .
   docker run -p 8000:8000 cognitive-user-twin
   ```

### API Endpoints

- **GET /health**: Check system status.
- **POST /simulate-review**: Generate a behavioral review based on user/item/context.
- **POST /recommend**: Get cognitive-ranked recommendations.
- **POST /user/update**: Update user trust and memory after an interaction.

### Architecture
- **core/**: The behavioral "brain" (engine, models, recommender, review_gen).
- **apps/api/**: FastAPI layer with service/router separation.
- **tests/**: Behavioral and core unit tests.

### Features
- Nigerian Contextual Realism (Lagos stress, Rural affordability).
- Episodic & Semantic Memory with Decay.
- Negativity Bias in Trust Drift.
- Transparent Behavioral Reasoning Traces.
