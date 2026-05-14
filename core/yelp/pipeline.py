import logging
import os
from typing import List, Dict, Set, Optional
from datetime import datetime
import numpy as np
from .models import (
    YelpUserRaw, YelpBusinessRaw, YelpReviewRaw, 
    BehavioralProfile, BehavioralFeatures, UserInteraction
)
from .loader import YelpStreamLoader

logger = logging.getLogger(__name__)

class YelpIngestionPipeline:
    """
    Production-grade pipeline for Yelp dataset ingestion and behavioral profiling.
    Uses a user-first sampling strategy to preserve coherent behavioral timelines.
    """
    
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.user_file = os.path.join(data_dir, "yelp_academic_dataset_user.json")
        self.business_file = os.path.join(data_dir, "yelp_academic_dataset_business.json")
        self.review_file = os.path.join(data_dir, "yelp_academic_dataset_review.json")
        
        self.loader = YelpStreamLoader()

    def run(self, sample_size: int = 1000, min_reviews: int = 10):
        """
        Executes the full ingestion and profiling pipeline.
        """
        logger.info(f"Starting Yelp ingestion pipeline. Target sample size: {sample_size}")
        
        # 1. Sample active users
        sampled_user_ids = self._sample_active_users(sample_size, min_reviews)
        logger.info(f"Sampled {len(sampled_user_ids)} users with at least {min_reviews} reviews.")
        
        # 2. Retrieve all associated reviews for these users
        user_reviews = self._retrieve_user_reviews(sampled_user_ids)
        logger.info(f"Retrieved {sum(len(r) for r in user_reviews.values())} reviews for sampled users.")
        
        # 3. Retrieve associated businesses
        business_ids = {r.business_id for reviews in user_reviews.values() for r in reviews}
        businesses = self._retrieve_businesses(business_ids)
        logger.info(f"Retrieved {len(businesses)} unique businesses.")
        
        # 4. Construct behavioral profiles and compute features
        profiles = self._build_behavioral_profiles(sampled_user_ids, user_reviews, businesses)
        logger.info(f"Constructed {len(profiles)} behavioral profiles.")
        
        # 5. Export processed data
        self._export_profiles(profiles)
        logger.info("Pipeline execution complete.")
        return profiles

    def _sample_active_users(self, limit: int, min_reviews: int) -> Set[str]:
        """Samples users based on activity level."""
        sampled_ids = set()
        for user in self.loader.stream_objects(self.user_file, YelpUserRaw):
            if user.review_count >= min_reviews:
                sampled_ids.add(user.user_id)
            if len(sampled_ids) >= limit:
                break
        return sampled_ids

    def _retrieve_user_reviews(self, user_ids: Set[str]) -> Dict[str, List[YelpReviewRaw]]:
        """Streams reviews and filters for sampled users."""
        user_reviews = {uid: [] for uid in user_ids}
        for review in self.loader.stream_objects(self.review_file, YelpReviewRaw):
            if review.user_id in user_ids:
                user_reviews[review.user_id].append(review)
        return user_reviews

    def _retrieve_businesses(self, business_ids: Set[str]) -> Dict[str, YelpBusinessRaw]:
        """Streams businesses and filters for those linked to user reviews."""
        businesses = {}
        for business in self.loader.stream_objects(self.business_file, YelpBusinessRaw):
            if business.business_id in business_ids:
                businesses[business.business_id] = business
        return businesses

    def _build_behavioral_profiles(
        self, 
        user_ids: Set[str], 
        user_reviews: Dict[str, List[YelpReviewRaw]], 
        businesses: Dict[str, YelpBusinessRaw]
    ) -> List[BehavioralProfile]:
        """Computes features and assembles profiles."""
        profiles = []
        for uid in user_ids:
            reviews = user_reviews.get(uid, [])
            if not reviews:
                continue
            
            # Sort reviews by date for temporal consistency
            reviews.sort(key=lambda x: x.date)
            
            interactions = []
            for r in reviews:
                interactions.append(UserInteraction(
                    business_id=r.business_id,
                    stars=r.stars,
                    text=r.text,
                    timestamp=datetime.strptime(r.date, "%Y-%m-%d %H:%M:%S"),
                    business_info=businesses.get(r.business_id)
                ))
            
            features = self._compute_behavioral_features(interactions)
            profiles.append(BehavioralProfile(
                user_id=uid,
                features=features,
                history=interactions
            ))
        return profiles

    def _compute_behavioral_features(self, interactions: List[UserInteraction]) -> BehavioralFeatures:
        """
        Calculates behavioral features from interaction history.
        """
        ratings = [i.stars for i in interactions]
        
        # Harshness: Average rating relative to 5
        harshness = 1.0 - (np.mean(ratings) / 5.0) if ratings else 0.5
        
        # Exploration: Unique businesses vs total visits
        biz_ids = [i.business_id for i in interactions]
        exploration = len(set(biz_ids)) / len(biz_ids) if biz_ids else 0.5
        
        # Loyalty: Repeat visits
        loyalty = 1.0 - exploration
        
        # Category Diversity: Unique categories
        categories = set()
        for i in interactions:
            if i.business_info and i.business_info.categories:
                cats = [c.strip() for c in i.business_info.categories.split(",")]
                categories.update(cats)
        diversity = min(len(categories) / 20.0, 1.0) # Normalized to max 20 categories
        
        # Temporal consistency: Std dev of days between reviews
        dates = [i.timestamp for i in interactions]
        if len(dates) > 2:
            intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            consistency = 1.0 / (1.0 + np.std(intervals) / 30.0) # Decay based on variance
        else:
            consistency = 0.5

        return BehavioralFeatures(
            rating_harshness=float(harshness),
            exploration_tendency=float(exploration),
            loyalty_score=float(loyalty),
            category_diversity=float(diversity),
            temporal_consistency=float(consistency)
        )

    def _export_profiles(self, profiles: List[BehavioralProfile]):
        """Exports processed profiles to JSON lines."""
        output_file = os.path.join(self.output_dir, "processed_profiles.jsonl")
        with open(output_file, 'w', encoding='utf-8') as f:
            for p in profiles:
                f.write(p.model_dump_json() + "\n")
