from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

# --- Raw Yelp Data Models (for streaming ingestion) ---

class YelpUserRaw(BaseModel):
    user_id: str
    name: str
    review_count: int
    yelping_since: str
    useful: int
    funny: int
    cool: int
    fans: int
    average_stars: float
    compliment_hot: int
    compliment_more: int
    compliment_profile: int
    compliment_cute: int
    compliment_list: int
    compliment_note: int
    compliment_plain: int
    compliment_cool: int
    compliment_funny: int
    compliment_writer: int
    compliment_photos: int

class YelpBusinessRaw(BaseModel):
    business_id: str
    name: str
    address: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float
    stars: float
    review_count: int
    is_open: int
    attributes: Optional[Dict[str, Any]] = None
    categories: Optional[str] = None
    hours: Optional[Dict[str, str]] = None

class YelpReviewRaw(BaseModel):
    review_id: str
    user_id: str
    business_id: str
    stars: int
    useful: int
    funny: int
    cool: int
    text: str
    date: str

# --- Processed Behavioral Models ---

class BehavioralFeatures(BaseModel):
    rating_harshness: float = 0.5  # Mean stars relative to average
    exploration_tendency: float = 0.5  # Unique categories visited
    loyalty_score: float = 0.0  # Repeat business visits
    emotionality: float = 0.5  # Sentiment intensity in text (to be computed)
    category_diversity: float = 0.0  # Entropy of categories
    price_sensitivity: float = 0.5  # Preference for $ vs $$$$
    temporal_consistency: float = 0.5  # Review frequency stability

class UserInteraction(BaseModel):
    business_id: str
    stars: int
    text: str
    timestamp: datetime
    business_info: Optional[YelpBusinessRaw] = None

class BehavioralProfile(BaseModel):
    user_id: str
    features: BehavioralFeatures
    history: List[UserInteraction]
    metadata: Dict[str, Any] = {}
