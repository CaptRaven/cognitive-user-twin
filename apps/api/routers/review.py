from fastapi import APIRouter, HTTPException
from apps.api.services.simulation_service import SimulationService
from core.models import Context, Item, Decision
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
sim_service = SimulationService()

class ReviewRequest(BaseModel):
    item: Item
    decision: Decision
    context: Optional[Context] = None

@router.post("/")
async def generate_review(request: ReviewRequest):
    """Manually generates a review based on a decision."""
    if not sim_service.user_profile:
        sim_service.initialize_twin()
        
    if sim_service.user_profile is None or sim_service.loop is None:
        raise HTTPException(status_code=500, detail="Failed to initialize twin")
        
    context = request.context or sim_service.environment.get_context()
    user_core = sim_service.loop._map_to_user_core(sim_service.user_profile)
    
    try:
        review = await sim_service.review_pipeline.generate_review(
            user_core,
            request.item,
            request.decision,
            context
        )
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
