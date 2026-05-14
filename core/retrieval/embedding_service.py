import logging
from typing import List, Union, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from core.yelp.models import BehavioralProfile, UserInteraction, YelpBusinessRaw

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Cognition-aware embedding service for behavioral AI.
    Generates embeddings for users, businesses, and interactions by 
    synthesizing behavioral summaries rather than raw text alone.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Initializing EmbeddingService with model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generic text embedding."""
        return self.model.encode(text, convert_to_numpy=True)

    def embed_user_behavior(self, profile: BehavioralProfile) -> np.ndarray:
        """
        Generates a behavioral embedding for a user profile.
        Synthesizes features like harshness, diversity, and consistency into a summary.
        """
        summary = (
            f"User with {profile.features.rating_harshness:.2f} rating harshness, "
            f"{profile.features.exploration_tendency:.2f} exploration tendency, "
            f"{profile.features.category_diversity:.2f} category diversity, and "
            f"{profile.features.temporal_consistency:.2f} temporal consistency. "
            f"Recent history includes {len(profile.history)} interactions."
        )
        return self.embed_text(summary)

    def embed_business(self, business: YelpBusinessRaw) -> np.ndarray:
        """
        Generates an embedding for a business.
        Combines name, categories, and attributes.
        """
        categories = business.categories if business.categories else "unknown"
        summary = f"Business: {business.name}. Categories: {categories}. Rating: {business.stars} stars."
        if business.attributes:
            attr_summary = ", ".join([f"{k}: {v}" for k, v in business.attributes.items() if isinstance(v, (str, bool))])
            summary += f" Attributes: {attr_summary}"
        return self.embed_text(summary)

    def embed_interaction(self, interaction: UserInteraction) -> np.ndarray:
        """
        Generates an embedding for a specific interaction (memory).
        Combines user sentiment, business context, and textual review.
        """
        biz_name = interaction.business_info.name if interaction.business_info else "unknown business"
        summary = (
            f"Interaction with {biz_name}. Rating: {interaction.stars} stars. "
            f"Experience text: {interaction.text[:200]}" # Truncate for efficiency
        )
        return self.embed_text(summary)

    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Computes cosine similarity between two embeddings."""
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
