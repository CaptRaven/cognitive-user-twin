import json
import logging
from typing import Generator, Any, Type, TypeVar
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class YelpStreamLoader:
    """
    Memory-efficient streaming loader for Yelp JSON dataset files.
    Each file is expected to be JSON-lines format (one JSON object per line).
    """
    
    @staticmethod
    def stream_objects(file_path: str, model: Type[T]) -> Generator[T, None, None]:
        """
        Streams JSON objects from a file and yields them as validated Pydantic models.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_idx, line in enumerate(f):
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        yield model(**data)
                    except Exception as e:
                        logger.error(f"Error parsing line {line_idx} in {file_path}: {e}")
                        continue
        except FileNotFoundError:
            logger.error(f"Dataset file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error streaming {file_path}: {e}")
            raise

    @staticmethod
    def count_lines(file_path: str) -> int:
        """Fast line counting for progress estimation."""
        with open(file_path, 'rb') as f:
            return sum(1 for _ in f)
