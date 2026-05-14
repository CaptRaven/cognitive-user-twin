import re

class ReviewPostprocessor:
    """
    Handles cleanup and realism normalization for generated reviews.
    """
    
    def process(self, text: str) -> str:
        """
        Cleans up the generated review text.
        """
        # Remove any "Review:" prefixes if the model included them
        text = re.sub(r'^Review:\s*', '', text, flags=re.IGNORECASE)
        
        # Remove surrounding quotes
        text = text.strip('"\'')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Basic sanity checks (e.g., length)
        if len(text) < 10:
            return "Experience was okay, but nothing special to report."
            
        return text
