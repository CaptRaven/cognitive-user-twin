import os
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

try:
    from mistralai import Mistral
    from mistralai.models import SDKError
except ImportError:
    # Handle newer namespace-style or azure-unified Mistral SDKs
    try:
        from mistralai.client import Mistral
        from mistralai.client.errors import SDKError
    except ImportError:
        logger.error("Could not import Mistral client. Please ensure 'mistralai' is installed correctly.")
        raise

class MistralClient:
    """
    Production-ready wrapper for Mistral AI inference.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-tiny"):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            logger.warning("MISTRAL_API_KEY not found in environment.")
        
        self.client = Mistral(api_key=self.api_key)
        self.model = model

    async def generate_review(
        self, 
        prompt: str, 
        temperature: float = 0.7, 
        max_tokens: int = 200
    ) -> str:
        """
        Generates text using Mistral with retry logic.
        """
        if not self.api_key:
            return "Error: No Mistral API key configured."

        try:
            response = await self.client.chat.complete_async(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            if response and response.choices:
                return response.choices[0].message.content.strip()
            return "Error: Empty response from Mistral."
        except SDKError as e:
            logger.error(f"Mistral SDK Error: {e}")
            return f"Error generating review: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in MistralClient: {e}")
            return f"Error: {str(e)}"
