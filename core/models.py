from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

# --- Enums ---

class ItemCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    BOOKS = "books"
    HOME = "home"
    BEAUTY = "beauty"
    SPORTS = "sports"
    TOYS = "toys"
    OTHER = "other"

class TimeOfDay(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

# --- Memory Models ---

class EpisodicMemory(BaseModel):
    """Specific interaction experiences with temporal and emotional context."""
    item_id: str
    sentiment: float = Field(ge=-1.0, le=1.0)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    decay_rate: float = 0.1 # Rate at which influence fades per day

    def get_current_influence(self) -> float:
        """Calculate influence after applying time-based decay."""
        days_passed = (datetime.now() - self.timestamp).total_seconds() / 86400
        # Exponential decay: Influence = Sentiment * Importance * e^(-decay * time)
        import math
        decay_factor = math.exp(-self.decay_rate * days_passed)
        return self.sentiment * self.importance * decay_factor

class SemanticMemory(BaseModel):
    """Stable learned beliefs and generalizations (e.g., Brand Trust, Category Affinity)."""
    concept: str # e.g., "brand:LuxAudio" or "category:electronics"
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=datetime.now)

class MemoryStore(BaseModel):
    """Managed container for episodic and semantic memories."""
    episodic: List[EpisodicMemory] = []
    semantic: Dict[str, SemanticMemory] = {}

# --- Core Models ---

class Context(BaseModel):
    time_of_day: TimeOfDay = TimeOfDay.MORNING
    is_weekend: bool = False
    device: str = "mobile"
    time_pressure: float = 0.0
    location_context: str = "Lagos"
    infrastructure_stress: float = 0.2
    economic_context: Optional[float] = None
    mood: Optional[float] = None
    recent_negative_interactions: List[str] = []

class Item(BaseModel):
    item_id: str
    name: str
    category: ItemCategory
    price: float
    features: Dict[str, float]
    brand: str
    brand_tier: float = 0.5
    rating: float = 0.0
    reviews_count: int = 0
    novelty: float = 0.5
    delivery_speed: float = 0.5

class UserProfile(BaseModel):
    user_id: str
    archetype: str
    preferences: Dict[str, float]
    budget_sensitivity: float
    brand_loyalty: float
    novelty_preference: float
    
    # Behavioral state
    mood: float = 0.5
    trust: float = 0.5
    fatigue: float = 0.0
    
    # Memory Subsystem
    memory: MemoryStore = Field(default_factory=MemoryStore)

class Decision(BaseModel):
    score: float
    label: str  # "buy", "skip", "consider"
    reasoning: List[str]
    factors: Dict[str, float]

class RecommendedItem(BaseModel):
    item: Item
    decision: Decision
    score: float
    explanation: str
    memory_influence: float = 0.5

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendedItem]
    context_snapshot: Dict[str, Any]

class Review(BaseModel):
    user_id: str
    item_id: str
    rating: int # 1-5 stars
    text: str
    tone: str
    satisfaction_score: float
    behavioral_factors: List[str]
    memory_influence: float = 0.5
    metadata: Dict[str, Any] = {}

# --- API Schemas ---

class SimulateReviewRequest(BaseModel):
    user: UserProfile
    item: Item
    context: Context

class RecommendRequest(BaseModel):
    user: UserProfile
    candidates: List[Item]
    context: Context
    top_n: int = 3

class UserUpdateRequest(BaseModel):
    user: UserProfile
    item: Item
    satisfaction: float
