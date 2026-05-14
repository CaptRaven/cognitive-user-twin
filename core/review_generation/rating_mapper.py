class RatingMapper:
    """
    Maps satisfaction scores to 1-5 star ratings with behavioral bias.
    """
    
    def map_rating(self, satisfaction_score: float, harshness: float = 0.5) -> int:
        """
        Calculates star rating. 
        Higher harshness makes it harder to get high stars.
        """
        # Adjusted score based on harshness
        # if harshness is 1.0 (very harsh), we subtract more
        # if harshness is 0.0 (very lenient), we subtract less or add
        bias = (0.5 - harshness) * 0.2
        adjusted_score = max(0.0, min(1.0, satisfaction_score + bias))
        
        if adjusted_score >= 0.85:
            return 5
        if adjusted_score >= 0.65:
            return 4
        if adjusted_score >= 0.45:
            return 3
        if adjusted_score >= 0.25:
            return 2
        return 1
