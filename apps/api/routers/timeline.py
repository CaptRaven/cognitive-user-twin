from fastapi import APIRouter
from apps.api.services.simulation_service import SimulationService

router = APIRouter()
sim_service = SimulationService()

@router.get("/")
async def get_timeline():
    """Returns the behavioral timeline of the twin."""
    return sim_service.get_timeline()
