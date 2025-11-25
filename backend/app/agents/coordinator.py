from typing import Dict, Any, List, AsyncGenerator, Tuple, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging
import uuid as uuid_lib

from app.agents.clarifier import ClarifierAgent
from app.agents.executor import ExecutorAgent
from app.agents.ranker import RankerAgent
from app.models.goal import Goal, GoalStatus, GoalType
from app.models.chat import Message
from app.services.temporal import get_temporal_client
from app.workflows.matching import GoalProcessingWorkflow

logger = logging.getLogger(__name__)

# Type for SSE events
EventType = Literal["stream_token", "stream_end", "status", "complete", "message"]
StructuredEvent = Tuple[EventType, Dict[str, Any]]

class CoordinatorAgent:
    """
    The 'Front Office' Agent.
    Responsibilities:
    1. Talk to the user (Clarification).
    2. Decide when the Goal is ready.
    3. Save the Goal to DB.
    4. Dispatch the Goal to the 'Back Office' (Temporal Worker).
    """
    
    def __init__(self):
        self.clarifier = ClarifierAgent()
        self.executor = ExecutorAgent()
        self.ranker = RankerAgent()

    async def get_ranked_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Retrieve and rank opportunities for a given goal.
        Used by the GET /api/opportunities endpoint.
        """
        try:
            ranked = await self.ranker.rank_opportunities(
                db=db,
                goal_id=goal_id,
                user_id=user_id,
                limit=limit
            )
            
            summary = await self.ranker.generate_summary(ranked)
            
            user_message = await self.clarifier.format_results_for_user(
                opportunities_count=len(ranked),
                summary=summary,
                status="completed"
            )
            
            return {
                "success": True,
                "opportunities": ranked,
                "summary": summary,
                "user_message": user_message,
                "total": len(ranked)
            }
            
        except Exception as e:
            logger.error(f"Error getting ranked opportunities: {e}")
            error_message = await self.clarifier.format_results_for_user(
                opportunities_count=0,
                status="error"
            )
            return {
                "success": False,
                "error": str(e),
                "user_message": error_message,
                "opportunities": []
            }

    async def refresh_goal_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        goal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Manually trigger a re-scrape/refresh for a goal.
        Used by the Temporal Refresh Workflow.
        """
        logger.info(f"Refreshing opportunities for goal {goal_id}")
        
        try:
            # We reuse the executor logic here for the refresh action
            opportunities = await self.executor.execute_search(db, goal_data)
            
            return {
                "success": True,
                "goal_id": str(goal_id),
                "new_opportunities": len(opportunities),
                "message": f"Found {len(opportunities)} new opportunities"
            }
            
        except Exception as e:
            logger.error(f"Error refreshing opportunities: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_questions_stream(self, initial_description: str) -> AsyncGenerator[str, None]:
        """Stream a conversational clarifying message (Initial Chat)"""
        try:
            preliminary_analysis = await self.clarifier.clarify_goal(initial_description)
            async for token in self.clarifier.generate_clarifying_questions_stream(
                initial_description, 
                preliminary_analysis
            ):
                yield token
            
        except Exception as e:
            logger.error(f"Error generating questions stream: {e}")
            yield "I'd love to help you find the right opportunities! Could you tell me a bit more about what you're looking for?"
    
    async def process_goal_with_answers_stream(
        self,
        db: AsyncSession,
        user_id: UUID,
        initial_description: str,
        qa_pairs: List[Dict[str, str]],
        conversation_id: str
    ) -> AsyncGenerator[StructuredEvent, None]:
        """
        The Main Chat Loop.
        1. Refine Goal based on answers.
        2. If Complete -> Save to DB -> Trigger Temporal -> Notify User.
        3. If Incomplete -> Ask next question.
        """
        try:
            # 1. Analyze Context
            preliminary_goal = await self.clarifier.clarify_goal(initial_description)
            
            latest_answer = (qa_pairs[-1]["answer"] if qa_pairs else "") or ""
            refined_goal = await self.clarifier.extract_partial_info(
                latest_answer,
                initial_description,
                preliminary_goal
            )

            # 2. Check Intent (Did user say "stop" or "hello"?)
            intent = self.clarifier.classify_intent(latest_answer)
            
            # 3. DECISION: Are we done clarifying?
            # We proceed if the goal is semantically complete AND the user isn't just saying "hi" or "stop"
            goal_is_ready = (
                self.clarifier.is_goal_complete(refined_goal) 
                and intent not in {"meta", "greeting", "acknowledgment", "cancel"}
            )

            if goal_is_ready:
                # --- PHASE A: PERSISTENCE ---
                # Generate Embedding for vector search
                goal_embedding = await self.clarifier.generate_goal_embedding(refined_goal)
                refined_goal["embedding"] = goal_embedding # Store for reference

                # Create the Goal Record
                goal = Goal(
                    user_id=user_id,
                    conversation_id=UUID(conversation_id),
                    description=initial_description,
                    goal_type=GoalType(refined_goal.get("goal_type", "job")),
                    filters=refined_goal,
                    embedding=goal_embedding,
                    status=GoalStatus.ACTIVE
                )
                db.add(goal)
                await db.commit()
                await db.refresh(goal)

                # --- PHASE B: EXECUTION (Async Handoff) ---
                try:
                    client = await get_temporal_client()
                    
                    await client.start_workflow(
                        GoalProcessingWorkflow.run,
                        args=[str(goal.id), str(user_id), initial_description],
                        id=f"goal-process-{goal.id}",
                        task_queue="genie-tasks"
                    )
                    
                    # --- PHASE C: USER FEEDBACK ---
                    # Stream a confirmation message
                    completion_message = f"I've understood your goal! I'm now deploying a **Deep Research Agent** to find {goal.goal_type.value} opportunities for you.\n\nThis involves scraping multiple sources and analyzing them, which can take a few minutes. You'll be notified when the report is ready."
                    
                    msg_id = str(uuid_lib.uuid4())
                    
                    # Stream tokens for UI effect
                    tokens = completion_message.split(" ")
                    for token in tokens:
                        yield ("stream_token", {"message_id": msg_id, "token": token + " "})
                    
                    # Save the assistant's message
                    assistant_msg = Message(
                        id=UUID(msg_id),
                        conversation_id=UUID(conversation_id),
                        role="assistant",
                        content=completion_message,
                        metadata_json={"type": "completion", "goal_id": str(goal.id)}
                    )
                    db.add(assistant_msg)
                    
                    # Update Conversation Status
                    from app.models.chat import Conversation
                    # We use execute/scalars for async session compatibility
                    result = await db.execute(select(Conversation).where(Conversation.id == UUID(conversation_id)))
                    conv = result.scalar_one_or_none()
                    if conv:
                        conv.status = "processing" # Set to processing, not completed yet
                        conv.goal_id = goal.id
                    
                    await db.commit()

                    yield ("stream_end", {
                        "message_id": msg_id, 
                        "content": completion_message, 
                        "created_at": assistant_msg.created_at.isoformat()
                    })
                    
                    # Signal frontend to refresh/redirect
                    yield ("complete", {"goal_id": str(goal.id)})
                    
                except Exception as e:
                    logger.error(f"Failed to trigger Temporal: {e}")
                    yield ("status", {"status": "error", "message": "Goal saved, but failed to start research worker."})
                
                return # <--- CRITICAL: EXIT HERE. Do not run the rest of the function.

            # 4. IF NOT READY: Continue Clarification Loop
            # Generate next single question
            next_question = await self.clarifier.generate_next_question(
                refined_goal,
                [] 
            )
            
            if not next_question:
                next_question = "Could you provide a bit more detail about what you're looking for?"
            
            message_id = str(uuid_lib.uuid4())
            full_content = ""
            
            # Stream the follow-up question
            async for token in self.clarifier.generate_clarifying_questions_stream(
                initial_description,
                refined_goal
            ):
                full_content += token
                yield ("stream_token", {
                    "message_id": message_id,
                    "token": token
                })
            
            # Save message to database
            assistant_message = Message(
                id=UUID(message_id),
                conversation_id=UUID(conversation_id),
                role="assistant",
                content=full_content,
                metadata_json={"type": "clarifying"}
            )
            db.add(assistant_message)
            await db.commit()
            
            yield ("stream_end", {
                "message_id": message_id,
                "content": full_content,
                "created_at": assistant_message.created_at.isoformat()
            })
                
        except Exception as e:
            logger.error(f"Error in process_goal_with_answers_stream: {e}", exc_info=True)
            yield ("status", {
                "status": "error",
                "message": "An error occurred while processing your goal",
                "metadata": {"error": str(e)}
            })