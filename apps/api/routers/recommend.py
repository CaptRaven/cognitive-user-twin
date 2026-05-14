from fastapi import APIRouter, HTTPException
from apps.api.services.simulation_service import SimulationService
from core.models import Context
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
sim_service = SimulationService()

class RecommendRequest(BaseModel):
    user_id: Optional[str] = None
    context: Optional[Context] = None
    top_k: int = 5

@router.post("/")
async def get_recommendation(request: RecommendRequest):
    """Manually requests a recommendation for the twin's current state."""
    if not sim_service.user_profile:
        sim_service.initialize_twin()
        
    if sim_service.user_profile is None:
        raise HTTPException(status_code=500, detail="Failed to initialize twin")
        
    context = request.context or sim_service.environment.get_context()
    
    try:
        results = await sim_service.rec_pipeline.recommend(
            sim_service.user_profile,
            context,
            top_k=request.top_k
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
