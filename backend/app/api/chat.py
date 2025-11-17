from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, AsyncGenerator
from uuid import UUID
import logging
import uuid as uuid_lib

from app.database import get_db, AsyncSessionLocal
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
from app.auth import get_current_user, get_user_email_from_token
from app.services.user_service import get_or_create_user
from app.services.streaming import (
    format_sse,
    status_event,
    stream_end_event,
    complete_event,
    message_event,
    error_event
)

router = APIRouter()
coordinator = CoordinatorAgent()
logger = logging.getLogger(__name__)


def generate_title_from_message(message: str, max_words: int = 6) -> str:
    """Generate a conversation title from the first few words of a message"""
    words = message.strip().split()[:max_words]
    title = ' '.join(words)
    if len(message.split()) > max_words:
        title += '...'
    return title


@router.post("/", response_class=StreamingResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """Create conversation and stream clarifying questions"""
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
    
    async def event_stream():
        """Generate SSE events for the initial conversation"""
        try:
            message_id = str(uuid_lib.uuid4())
            full_content = ""
            
            # Stream clarifying questions token by token
            async for token in coordinator.generate_questions_stream(conversation_data.initial_message):
                full_content += token
                yield format_sse("stream_token", {
                    "message_id": message_id,
                    "token": token
                })
            
            # Save complete message to database
            async with AsyncSessionLocal() as session:
                assistant_message = Message(
                    id=UUID(message_id),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_content,
                    metadata_json={"type": "clarifying"}
                )
                session.add(assistant_message)
                await session.commit()
                await session.refresh(assistant_message)
                
                # Send stream_end event
                yield stream_end_event(
                    message_id,
                    full_content,
                    assistant_message.created_at.isoformat()
                )
                
                # Send conversation ID so frontend knows where to navigate
                yield format_sse("conversation_created", {
                    "conversation_id": str(conversation.id),
                    "status": "clarifying"
                })
                
        except Exception as e:
            logger.error(f"Error streaming initial message: {e}", exc_info=True)
            yield error_event("An error occurred while processing your message")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


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


@router.post("/{conversation_id}/answer-questions", response_class=StreamingResponse)
async def answer_questions(
    conversation_id: UUID,
    answers_data: AnswerQuestionsRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user)
):
    """Answer clarifying questions and stream response/search progress"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify ownership
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Save user's answer
    answers_text = "\n\n".join([qa.answer for qa in answers_data.answers])
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=answers_text,
        metadata_json={"type": "question_answers", "answers": [qa.dict() for qa in answers_data.answers]}
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    async def event_stream():
        """Generate SSE events for goal processing"""
        try:
            # First, emit the user's message so frontend sees it immediately
            yield message_event({
                "id": str(user_message.id),
                "conversation_id": str(conversation_id),
                "role": "user",
                "content": user_message.content,
                "metadata": user_message.metadata_json,
                "created_at": user_message.created_at.isoformat()
            })
            
            async with AsyncSessionLocal() as session:
                # Get initial message for context
                messages_result = await session.execute(
                    select(Message)
                    .where(Message.conversation_id == conversation_id)
                    .order_by(Message.created_at)
                )
                messages = messages_result.scalars().all()
                initial_message = next((m.content for m in messages if m.role == "user"), "")
                
                qa_pairs = [{"question": qa.question, "answer": qa.answer} for qa in answers_data.answers]
                
                # Process the goal with answers - this will yield events
                async for event_type, event_data in coordinator.process_goal_with_answers_stream(
                    session,
                    user_id,
                    initial_message,
                    qa_pairs,
                    str(conversation_id)
                ):
                    yield format_sse(event_type, event_data)
                
        except Exception as e:
            logger.error(f"Error processing answers: {e}", exc_info=True)
            yield error_event("An error occurred while processing your answers")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
