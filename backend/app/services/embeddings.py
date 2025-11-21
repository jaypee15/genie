from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings
import logging

logger = logging.getLogger(__name__)

embeddings_client = GoogleGenerativeAIEmbeddings(
    google_api_key=settings.google_api_key,
    model="models/embedding-001",
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

