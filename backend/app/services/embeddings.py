from typing import List
from langchain_openai import OpenAIEmbeddings
from app.config import settings
import logging

logger = logging.getLogger(__name__)

embeddings_client = OpenAIEmbeddings(
    api_key=settings.openai_api_key,
    model="text-embedding-3-small",
)


async def generate_embedding(text: str) -> List[float]:
    try:
        return await embeddings_client.aembed_query(text)
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    try:
        return await embeddings_client.aembed_documents(texts)
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise

