# Cognitive User Twin Platform

## Production-Ready AI Behavioral Simulation & Recommendation

A persistent behavioral cognition simulation platform that models a "living" digital human with evolving preferences, memories, emotions, and decision-making patterns. This system satisfies both the **Cognitive User Twin** and **Intelligent Recommendation Engine** competition tasks.

***

## Quick Start

### 1. Backend Setup (FastAPI)

```bash
# From project root
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the API in module mode
python3 -m apps.api.main
```

The API will be available at `http://localhost:8000`. You can view the OpenAPI docs at `http://localhost:8000/docs`.

### 2. Frontend Setup (Next.js)

```bash
# From apps/web directory
cd apps/web
npm install
npm run dev
```

The **Living Cognitive Twin Monitor** will be available at `http://localhost:3000`.

***

## Core Architecture

### Phase 1 — Vector Store Population

The system uses **ChromaDB** populated with 140+ realistic business candidates (Nigerian archetypes, fusion restaurants, quiet cafes).

- **Script**: `python3 scripts/populate_vector_store.py`
- **Metadata**: Includes price, ambiance, delivery speed, and **stress-comfort score**.

### Phase 2 — Autonomous Life Simulation

The "Twin" lives in a dynamic environment ([environment.py](core/simulation/environment.py)) where events like traffic frustration, budget pressure, and hunger trigger cognitive decisions.

- **State Evolution**: Implements negativity bias, loyalty formation, and decision fatigue.
- **Memory**: Persistent episodic and semantic memory with temporal decay.

### Phase 3 — FastAPI Production API

- `POST /simulate/start`: Initialize a new twin.
- `POST /simulate/step`: Advance simulation by 1 hour.
- `GET /timeline`: Live behavioral feed with neural traces.
- `GET /analytics`: Loyalty trends and trust drift metrics.

### Phase 4 — Demo Visualization UI

A modern "Living Monitor" built with **Next.js**, **TailwindCSS**, and **Framer Motion**.

- **Live State**: Real-time mood, fatigue, and loyalty tracking.
- **Behavioral Timeline**: A scrolling feed of the twin's daily life.
- **Cognition Panel**: Visible reasoning chains and influence vectors for every decision.

***

## 🐳 Docker Deployment

To run the backend using Docker:

```bash
# Build the image
docker build -t twin-backend .

# Run with environment variables
docker run -d \
  --name twin-backend \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  twin-backend
```

***

## 📊 Evaluation & Analytics

The platform tracks:

- **Behavioral Consistency**: How fatigue affects convenience preference.
- **Trust Drift**: Loyalty evolution based on service quality.
- **Exploration Adaptation**: Novelty seeking vs. settlement behavior.
- **Cognitive Auditing**: Explainable AI traces for every recommendation.

***

## 🛠 Tech Stack

- **Backend**: FastAPI, Pydantic, NumPy
- **AI/LLM**: Mistral AI (Review Generation), SentenceTransformers (Embeddings)
- **Database**: ChromaDB (Vector Store)
- **Frontend**: Next.js 15, TailwindCSS, Framer Motion, Lucide React
- **Infrastructure**: Docker, Python 3.12

