from core.engine import CognitiveEngine
from core.recommender import RecommendationEngine
from core.review_generation.review_pipeline import ReviewGenerationPipeline
from core.models import (
    SimulateReviewRequest, 
    RecommendRequest, 
    UserUpdateRequest,
    Review,
    RecommendationResponse,
    UserProfile
)
from apps.api.logger import logger
from apps.api.config import settings

class CognitiveService:
    def __init__(self):
        self.cog_engine = CognitiveEngine(noise=settings.COGNITIVE_NOISE)
        self.rec_engine = RecommendationEngine(self.cog_engine)
        self.review_gen = ReviewGenerationPipeline(mistral_api_key=settings.MISTRAL_API_KEY)

    async def simulate_review(self, request: SimulateReviewRequest) -> Review:
        logger.info(f"Simulating review for user {request.user.user_id} and item {request.item.item_id}")
        decision = self.cog_engine.evaluate(request.user, request.item, request.context)
        review = await self.review_gen.generate_review(request.user, request.item, decision, request.context)
        logger.info(f"Generated review with satisfaction score: {review.satisfaction_score}")
        return review

    async def get_recommendations(self, request: RecommendRequest) -> RecommendationResponse:
        logger.info(f"Getting recommendations for user {request.user.user_id} with {len(request.candidates)} candidates")
        return self.rec_engine.recommend(
            request.user, 
            request.candidates, 
            request.context, 
            request.top_n
        )

    async def update_user_behavior(self, request: UserUpdateRequest) -> UserProfile:
        logger.info(f"Updating user behavior for user {request.user.user_id} after interaction with item {request.item.item_id}")
        self.cog_engine.update_state(request.user, request.item, request.satisfaction)
        return request.user
