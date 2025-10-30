from openai import AsyncOpenAI
from typing import List, Union
from app.config import settings
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_embedding(text: str) -> List[float]:
    try:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    try:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
            encoding_format="float"
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise

