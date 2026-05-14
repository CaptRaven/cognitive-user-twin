from fastapi import APIRouter, Depends, HTTPException
from apps.api.services.simulation_service import SimulationService
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()
sim_service = SimulationService()

class StartRequest(BaseModel):
    user_id: str = "demo_user"

@router.post("/start")
async def start_simulation(request: StartRequest):
    """Initializes the autonomous twin."""
    profile = sim_service.initialize_twin(request.user_id)
    return {"status": "initialized", "profile": profile}

@router.post("/step")
async def step_simulation():
    """Advances the simulation by 1 hour and processes events."""
    results = await sim_service.step()
    return {"status": "success", "events": results, "state": sim_service.get_state()}

@router.get("/state")
async def get_state():
    """Returns current twin and environment state."""
    return sim_service.get_state()
