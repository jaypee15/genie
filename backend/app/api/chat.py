from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
import logging
import json
from ably import AblyRest
import inspect

from app.database import get_db
from app.models.chat import Conversation, Message
from app.models.user import User
from app.models.goal import Goal, GoalStatus, GoalType
from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageCreate,
    MessageResponse,
    AnswerQuestionsRequest
)
from app.agents.coordinator import CoordinatorAgent
from app.services.ably_service import ably_service
from app.auth import get_current_user, get_user_email_from_token
from app.services.user_service import get_or_create_user
from app.config import settings

router = APIRouter()
coordinator = CoordinatorAgent()
logger = logging.getLogger(__name__)
ably_auth = AblyRest(key=settings.ably_api_key)


def generate_title_from_message(message: str, max_words: int = 6) -> str:
    """Generate a conversation title from the first few words of a message"""
    words = message.strip().split()[:max_words]
    title = ' '.join(words)
    if len(message.split()) > max_words:
        title += '...'
    return title


@router.get("/realtime/token")
async def get_ably_token(user_id: UUID = Depends(get_current_user)):
    """Generate Ably token with subscribe-only capability for user's conversations"""
    capability = {"conversation:*": ["subscribe"]}
    token_request = ably_auth.auth.create_token_request(
        token_params={
            "client_id": str(user_id),
            "capability": json.dumps(capability),
            "ttl": 3600000,  # 1 hour in ms
        }
    )
    # Support both sync and async return types
    if inspect.isawaitable(token_request):
        token_request = await token_request
    # Ensure JSON serializable output
    if hasattr(token_request, "to_dict"):
        return token_request.to_dict()  # type: ignore[attr-defined]
    if isinstance(token_request, dict):
        return token_request
    # Fallback: try to coerce to dict
    try:
        return dict(token_request)  # type: ignore[arg-type]
    except Exception:
        return token_request


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    # Get or create user on first conversation
    email = get_user_email_from_token(credentials.credentials)
    if email:
        await get_or_create_user(db, user_id, email)
    
    # Generate title from initial message
    title = generate_title_from_message(conversation_data.initial_message)
    
    conversation = Conversation(user_id=user_id, status="clarifying", title=title)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=conversation_data.initial_message
    )
    db.add(user_message)
    await db.commit()
    
    background_tasks.add_task(
        process_initial_message,
        str(conversation.id),
        conversation_data.initial_message
    )
    
    return conversation


async def process_initial_message(conversation_id: str, initial_message: str):
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            conversational_message = await coordinator.generate_questions(initial_message)
            
            assistant_message = Message(
                conversation_id=UUID(conversation_id),
                role="assistant",
                content=conversational_message,
                metadata_json={"type": "clarifying"}
            )
            db.add(assistant_message)
            await db.commit()
            
            await ably_service.publish_message(conversation_id, {
                "type": "message",
                "message": {
                    "id": str(assistant_message.id),
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": assistant_message.content,
                    "metadata": assistant_message.metadata_json,
                    "created_at": assistant_message.created_at.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing initial message: {e}")


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    return ConversationWithMessages(
        **conversation.__dict__,
        messages=[MessageResponse.model_validate(m) for m in messages]
    )


@router.post("/{conversation_id}/message", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content,
        metadata_json=message_data.metadata_json
    )
    db.add(message)
    
    conversation.updated_at = message.created_at
    
    await db.commit()
    await db.refresh(message)
    
    return message


@router.post("/{conversation_id}/answer-questions")
async def answer_questions(
    conversation_id: UUID,
    answers_data: AnswerQuestionsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    answers_text = "\n".join([f"Q: {qa.question}\nA: {qa.answer}" for qa in answers_data.answers])
    
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=answers_text,
        metadata_json={"type": "question_answers", "answers": [qa.dict() for qa in answers_data.answers]}
    )
    db.add(user_message)
    
    conversation.status = "processing"
    await db.commit()
    
    background_tasks.add_task(
        process_goal_from_answers,
        str(conversation.id),
        str(conversation.user_id),
        answers_data.answers
    )
    
    return {"message": "Processing your goal..."}


async def process_goal_from_answers(conversation_id: str, user_id: str, answers: List):
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Conversation).where(Conversation.id == UUID(conversation_id))
            )
            conversation = result.scalar_one_or_none()
            
            messages_result = await db.execute(
                select(Message)
                .where(Message.conversation_id == UUID(conversation_id))
                .order_by(Message.created_at)
            )
            messages = messages_result.scalars().all()
            
            initial_message = next((m.content for m in messages if m.role == "user"), "")
            
            processing_message = Message(
                conversation_id=UUID(conversation_id),
                role="assistant",
                content="Great! I'm now searching for opportunities that match your criteria...",
                metadata_json={"type": "status", "status": "processing"}
            )
            db.add(processing_message)
            await db.commit()
            
            await ably_service.publish_message(conversation_id, {
                "type": "message",
                "message": {
                    "id": str(processing_message.id),
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": processing_message.content,
                    "metadata": processing_message.metadata_json,
                    "created_at": processing_message.created_at.isoformat()
                }
            })
            
            qa_pairs = [{"question": qa.question, "answer": qa.answer} for qa in answers]
            goal_result = await coordinator.process_goal_with_answers(
                db, UUID(user_id), initial_message, qa_pairs, conversation_id
            )
            
            if goal_result["success"]:
                goal_id = goal_result["goal_id"]
                
                stmt = select(Conversation).where(Conversation.id == UUID(conversation_id))
                result = await db.execute(stmt)
                conv = result.scalar_one_or_none()
                if conv:
                    conv.goal_id = UUID(goal_id)
                    conv.status = "completed"
                    conv.title = initial_message[:50]
                    await db.commit()
                
                completion_message = Message(
                    conversation_id=UUID(conversation_id),
                    role="assistant",
                    content=goal_result["user_message"],
                    metadata_json={"type": "completion", "goal_id": goal_id}
                )
                db.add(completion_message)
                await db.commit()
                
                await ably_service.publish_message(conversation_id, {
                    "type": "message",
                    "message": {
                        "id": str(completion_message.id),
                        "conversation_id": conversation_id,
                        "role": "assistant",
                        "content": completion_message.content,
                        "metadata": completion_message.metadata_json,
                        "created_at": completion_message.created_at.isoformat()
                    }
                })
                
                await ably_service.publish_complete(
                    conversation_id,
                    goal_id,
                    goal_result.get("opportunities_found", 0)
                )
            
        except Exception as e:
            logger.error(f"Error processing goal from answers: {e}")
            
            error_message = Message(
                conversation_id=UUID(conversation_id),
                role="assistant",
                content="I encountered an error while processing your goal. Please try again.",
                metadata_json={"type": "error"}
            )
            db.add(error_message)
            await db.commit()


