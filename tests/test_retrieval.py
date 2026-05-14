import pytest
import asyncio
from core.retrieval.embedding_service import EmbeddingService
from core.retrieval.chroma_store import ChromaStore
from core.retrieval.candidate_retriever import CandidateRetriever, MemoryRetriever
from core.retrieval.reranker import BehavioralReranker
from core.yelp.models import BehavioralProfile, BehavioralFeatures
from core.engine import CognitiveEngine
from core.models import Context
import shutil
import os

@pytest.fixture
def test_data_dir():
    path = "data/test_chroma"
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

@pytest.mark.asyncio
async def test_retrieval_flow(test_data_dir):
    # 1. Setup services
    embedding_service = EmbeddingService()
    chroma_store = ChromaStore(persist_directory=test_data_dir)
    cog_engine = CognitiveEngine()
    
    candidate_retriever = CandidateRetriever(embedding_service, chroma_store)
    memory_retriever = MemoryRetriever(embedding_service, chroma_store)
    reranker = BehavioralReranker(cog_engine)
    
    # 2. Seed test data
    biz_id = "test_biz_1"
    biz_emb = embedding_service.embed_text("High-quality Italian restaurant in Lagos").tolist()
    chroma_store.add_businesses(
        ids=[biz_id],
        embeddings=[biz_emb],
        metadatas=[{"name": "Luigi's Italian", "stars": 4.5, "review_count": 100}]
    )
    
    # 3. Create a test user profile
    user_profile = BehavioralProfile(
        user_id="test_user_1",
        features=BehavioralFeatures(
            rating_harshness=0.2,
            exploration_tendency=0.8,
            loyalty_score=0.2,
            category_diversity=0.7
        ),
        history=[]
    )
    
    # 4. Retrieve candidates
    candidates = await candidate_retriever.retrieve_candidates(user_profile, n_results=1)
    assert len(candidates) > 0
    assert candidates[0]["id"] == biz_id
    
    # 5. Rerank
    context = Context(location_context="Lagos", infrastructure_stress=0.2)
    reranked = reranker.rerank(user_profile, candidates, context)
    
    assert len(reranked) > 0
    assert "final_score" in reranked[0]
    assert "reasoning" in reranked[0]
    
    print("\n✓ Retrieval and Reranking flow verified.")

if __name__ == "__main__":
    # For manual verification if needed
    asyncio.run(test_retrieval_flow("data/test_chroma_manual"))
