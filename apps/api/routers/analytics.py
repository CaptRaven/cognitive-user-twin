from fastapi import APIRouter
from apps.api.services.simulation_service import SimulationService

router = APIRouter()
sim_service = SimulationService()

@router.get("/")
async def get_analytics():
    """Returns behavioral analytics and metrics."""
    return sim_service.get_analytics()
