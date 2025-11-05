from ably import AblyRest
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AblyService:
    def __init__(self):
        self.client = AblyRest(key=settings.ably_api_key)
    
    async def publish_message(self, conversation_id: str, message_data: dict):
        """Publish a new message to the conversation channel"""
        try:
            channel = self.client.channels.get(f"conversation:{conversation_id}")
            await channel.publish(name="message", data=message_data)
            logger.info(f"Published message to conversation:{conversation_id}")
        except Exception as e:
            logger.error(f"Error publishing message to Ably: {e}")
    
    async def publish_status(self, conversation_id: str, status: str, message: str, metadata: dict = None):
        """Publish status update to the conversation channel"""
        try:
            channel = self.client.channels.get(f"conversation:{conversation_id}")
            await channel.publish(name="status", data={
                "status": status,
                "message": message,
                "metadata": metadata or {}
            })
            logger.info(f"Published status to conversation:{conversation_id} - {status}")
        except Exception as e:
            logger.error(f"Error publishing status to Ably: {e}")
    
    async def publish_complete(self, conversation_id: str, goal_id: str, opportunities_count: int):
        """Publish completion event to the conversation channel"""
        try:
            channel = self.client.channels.get(f"conversation:{conversation_id}")
            await channel.publish(name="complete", data={
                "goal_id": goal_id,
                "opportunities_count": opportunities_count
            })
            logger.info(f"Published completion to conversation:{conversation_id}")
        except Exception as e:
            logger.error(f"Error publishing completion to Ably: {e}")


ably_service = AblyService()

