import logging
from temporalio.client import Client
from app.config import settings

logger  = logging.getLogger(__name__)

async def get_temporal_client() -> Client:
    """
    Connect to Temporal.
    """

    target_host = settings.temporal_address or "localhost:7233"
    namespace = settings.temporal_namespace or "default"
    api_key = settings.temporal_api_key

    use_tls = settings.temporal_use_tls


    try: 
        client = await Client.connect(
            target_host,
            namespace=namespace,
            api_key=api_key,
            tls=use_tls,
        )
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Temporal at {target_host}: {e}")

