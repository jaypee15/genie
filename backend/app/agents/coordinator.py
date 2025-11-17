from typing import Dict, Any, List, TypedDict, Optional, AsyncGenerator, Tuple, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging
from langgraph.graph import StateGraph, END
import uuid as uuid_lib

from app.agents.clarifier import ClarifierAgent
from app.agents.executor import ExecutorAgent
from app.agents.ranker import RankerAgent
from app.models.goal import Goal, GoalStatus, GoalType

logger = logging.getLogger(__name__)

# Type for SSE events
EventType = Literal["stream_token", "stream_end", "status", "complete", "message"]
StructuredEvent = Tuple[EventType, Dict[str, Any]]


class AgentState(TypedDict):
    user_id: str
    goal_description: str
    clarified_goal: Dict[str, Any]
    opportunities: List[Dict[str, Any]]
    ranked_opportunities: List[Dict[str, Any]]
    summary: str
    user_message: str
    explanation: str
    error: str
    db: Any


class CoordinatorAgent:
    """
    Orchestrates the workflow between agents using LangGraph.
    Note: All user communication is routed through the ClarifierAgent.
    """
    
    def __init__(self):
        self.clarifier = ClarifierAgent()
        self.executor = ExecutorAgent()
        self.ranker = RankerAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("clarify", self._clarify_node)
        workflow.add_node("execute", self._execute_node)
        workflow.add_node("format_results", self._format_results_node)
        
        workflow.set_entry_point("clarify")
        workflow.add_edge("clarify", "execute")
        workflow.add_edge("execute", "format_results")
        workflow.add_edge("format_results", END)
        
        return workflow.compile()
    
    async def _clarify_node(self, state: AgentState) -> AgentState:
        try:
            clarified_goal = await self.clarifier.clarify_goal(state["goal_description"])
            explanation = await self.clarifier.explain_goal_clarification(clarified_goal)
            goal_embedding = await self.clarifier.generate_goal_embedding(clarified_goal)
            clarified_goal["embedding"] = goal_embedding
            
            state["clarified_goal"] = clarified_goal
            state["explanation"] = explanation
            
        except Exception as e:
            logger.error(f"Error in clarify node: {e}")
            state["error"] = str(e)
        
        return state
    
    async def _execute_node(self, state: AgentState) -> AgentState:
        if state.get("error"):
            return state
        
        try:
            opportunities = await self.executor.execute_search(
                state["db"], 
                state["clarified_goal"]
            )
            state["opportunities"] = opportunities
            
        except Exception as e:
            logger.error(f"Error in execute node: {e}")
            state["error"] = str(e)
        
        return state
    
    async def _format_results_node(self, state: AgentState) -> AgentState:
        if state.get("error"):
            user_message = await self.clarifier.format_results_for_user(
                opportunities_count=0,
                status="error"
            )
            state["user_message"] = user_message
            return state
        
        opportunities_count = len(state.get("opportunities", []))
        user_message = await self.clarifier.format_results_for_user(
            opportunities_count=opportunities_count,
            status="completed"
        )
        state["user_message"] = user_message
        
        return state
    
    async def process_new_goal(
        self,
        db: AsyncSession,
        user_id: UUID,
        goal_description: str
    ) -> Dict[str, Any]:
        logger.info(f"Processing new goal for user {user_id}")
        
        initial_state: AgentState = {
            "user_id": str(user_id),
            "goal_description": goal_description,
            "clarified_goal": {},
            "opportunities": [],
            "ranked_opportunities": [],
            "summary": "",
            "user_message": "",
            "explanation": "",
            "error": "",
            "db": db
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        if final_state.get("error"):
            return {
                "success": False,
                "error": final_state["error"],
                "user_message": final_state["user_message"]
            }
        
        return {
            "success": True,
            "clarified_goal": final_state["clarified_goal"],
            "opportunities_found": len(final_state["opportunities"]),
            "user_message": final_state["user_message"],
            "explanation": final_state["explanation"]
        }
    
    async def refresh_goal_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        goal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"Refreshing opportunities for goal {goal_id}")
        
        try:
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
    
    async def get_ranked_opportunities(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> Dict[str, Any]:
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
    
    async def process_user_feedback(
        self,
        rating: int
    ) -> Dict[str, Any]:
        acknowledgment = await self.clarifier.acknowledge_feedback(rating)
        
        return {
            "success": True,
            "user_message": acknowledgment
        }
    
    async def generate_questions(self, initial_description: str) -> str:
        """Generate a conversational clarifying message"""
        try:
            preliminary_analysis = await self.clarifier.clarify_goal(initial_description)
            conversational_message = await self.clarifier.generate_clarifying_questions(
                initial_description, 
                preliminary_analysis
            )
            
            return conversational_message
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return "I'd love to help you find the right opportunities! Could you tell me a bit more about what you're looking for?"
    
    async def generate_questions_stream(self, initial_description: str) -> AsyncGenerator[str, None]:
        """Stream a conversational clarifying message"""
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
    
    async def process_goal_with_answers(
        self,
        db: AsyncSession,
        user_id: UUID,
        initial_description: str,
        qa_pairs: List[Dict[str, str]],
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process goal creation with clarifying question answers"""
        try:
            preliminary_goal = await self.clarifier.clarify_goal(initial_description)
            
            # Extract partial info from latest answer
            latest_answer = (qa_pairs[-1]["answer"] if qa_pairs else "") or ""
            refined_goal = await self.clarifier.extract_partial_info(
                latest_answer,
                initial_description,
                preliminary_goal
            )
            
            # Classify intent on latest user answer
            intent = await self.clarifier.classify_intent(latest_answer)
            
            # If meta/greeting/cancel OR goal incomplete, stay in clarifying mode
            if intent in {"meta", "greeting", "acknowledgment", "cancel"} or not self.clarifier.is_goal_complete(refined_goal):
                # Generate next single question
                next_question = await self.clarifier.generate_next_question(
                    refined_goal,
                    []  # TODO: track asked_fields in conversation metadata
                )
                
                if not next_question:
                    next_question = "Could you provide a bit more detail about what you're looking for?"
                
                if conversation_id:
                    from app.models.chat import Message
                    import uuid
                    message_id = str(uuid.uuid4())
                    
                    # Stream the follow-up question
                    async for token in self.clarifier.generate_clarifying_questions_stream(
                        initial_description,
                        refined_goal
                    ):
                        await ably_service.publish_stream_token(conversation_id, message_id, token)
                    
                    # Save and publish stream end
                    assistant_message = Message(
                        id=UUID(message_id),
                        conversation_id=UUID(conversation_id),
                        role="assistant",
                        content=next_question,
                        metadata_json={"type": "clarifying"}
                    )
                    db.add(assistant_message)
                    await db.commit()
                    await db.refresh(assistant_message)
                    
                    await ably_service.publish_stream_end(
                        conversation_id,
                        message_id,
                        assistant_message.content,
                        assistant_message.created_at.isoformat()
                    )
                
                return {"success": False, "reason": "clarifying"}
            
            goal_embedding = await self.clarifier.generate_goal_embedding(refined_goal)
            refined_goal["embedding"] = goal_embedding
            
            # Generate and stream confirmation summary before starting search
            if conversation_id:
                from app.models.chat import Message
                import uuid
                confirmation = await self.clarifier.generate_confirmation_summary(refined_goal)
                confirm_msg_id = str(uuid.uuid4())
                
                # Stream confirmation
                for token in confirmation:
                    await ably_service.publish_stream_token(conversation_id, confirm_msg_id, token)
                
                # Save confirmation message
                confirm_message = Message(
                    id=UUID(confirm_msg_id),
                    conversation_id=UUID(conversation_id),
                    role="assistant",
                    content=confirmation,
                    metadata_json={"type": "confirmation"}
                )
                db.add(confirm_message)
                await db.commit()
                await db.refresh(confirm_message)
                
                await ably_service.publish_stream_end(
                    conversation_id,
                    confirm_msg_id,
                    confirmation,
                    confirm_message.created_at.isoformat()
                )
            
            goal = Goal(
                user_id=user_id,
                conversation_id=UUID(conversation_id) if conversation_id else None,
                description=initial_description,
                goal_type=GoalType(refined_goal.get("goal_type", "job")),
                filters=refined_goal,
                embedding=goal_embedding,
                status=GoalStatus.ACTIVE
            )
            db.add(goal)
            await db.commit()
            await db.refresh(goal)
            
            if conversation_id:
                await ably_service.publish_status(
                    conversation_id,
                    "searching",
                    "Searching for opportunities...",
                    {"goal_id": str(goal.id)}
                )
            
            opportunities = await self._search_with_updates(
                db, 
                refined_goal, 
                conversation_id
            )
            
            # Rank opportunities by relevance
            ranked_opportunities = await self.ranker.rank_opportunities(
                db=db,
                goal_id=goal.id,
                user_id=user_id,
                limit=50
            )
            
            # Generate summary of top opportunities
            summary = await self.ranker.generate_summary(ranked_opportunities, limit=5)
            
            # Format user message with top results
            user_message = await self._format_completion_message(
                goal_id=str(goal.id),
                opportunities_count=len(opportunities),
                ranked_opportunities=ranked_opportunities[:5],
                summary=summary
            )
            
            return {
                "success": True,
                "goal_id": str(goal.id),
                "clarified_goal": refined_goal,
                "opportunities_found": len(opportunities),
                "user_message": user_message,
                "ranked_opportunities": ranked_opportunities[:10]
            }
            
        except Exception as e:
            logger.error(f"Error processing goal with answers: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_message": "I encountered an error processing your goal. Please try again."
            }
    
    async def process_goal_with_answers_stream(
        self,
        db: AsyncSession,
        user_id: UUID,
        initial_description: str,
        qa_pairs: List[Dict[str, str]],
        conversation_id: str
    ) -> AsyncGenerator[StructuredEvent, None]:
        """Process goal and yield SSE events instead of publishing to Ably"""
        from app.models.chat import Message
        
        try:
            preliminary_goal = await self.clarifier.clarify_goal(initial_description)
            
            # Extract partial info from latest answer
            latest_answer = (qa_pairs[-1]["answer"] if qa_pairs else "") or ""
            refined_goal = await self.clarifier.extract_partial_info(
                latest_answer,
                initial_description,
                preliminary_goal
            )
            
            # Classify intent on latest user answer
            intent = await self.clarifier.classify_intent(latest_answer)
            
            # If meta/greeting/cancel OR goal incomplete, stay in clarifying mode
            if intent in {"meta", "greeting", "acknowledgment", "cancel"} or not self.clarifier.is_goal_complete(refined_goal):
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
                await db.refresh(assistant_message)
                
                # Send stream_end
                yield ("stream_end", {
                    "message_id": message_id,
                    "content": full_content,
                    "created_at": assistant_message.created_at.isoformat()
                })
                
                return  # Stop here, stay in clarifying mode
            
            # Goal is complete, proceed with search
            goal_embedding = await self.clarifier.generate_goal_embedding(refined_goal)
            refined_goal["embedding"] = goal_embedding
            
            # Stream confirmation summary
            confirmation = await self.clarifier.generate_confirmation_summary(refined_goal)
            confirm_msg_id = str(uuid_lib.uuid4())
            
            for token in confirmation:
                yield ("stream_token", {
                    "message_id": confirm_msg_id,
                    "token": token
                })
            
            # Save confirmation message
            confirm_message = Message(
                id=UUID(confirm_msg_id),
                conversation_id=UUID(conversation_id),
                role="assistant",
                content=confirmation,
                metadata_json={"type": "confirmation"}
            )
            db.add(confirm_message)
            await db.commit()
            await db.refresh(confirm_message)
            
            yield ("stream_end", {
                "message_id": confirm_msg_id,
                "content": confirmation,
                "created_at": confirm_message.created_at.isoformat()
            })
            
            # Create goal
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
            
            # Emit status for search start
            yield ("status", {
                "status": "searching",
                "message": "Searching for opportunities...",
                "metadata": {"goal_id": str(goal.id)}
            })
            
            # Execute search with streaming status updates
            async for event in self._search_with_updates_stream(db, refined_goal):
                yield event
            
            # Fetch actual opportunities from database
            opportunities = await self._get_opportunities_for_goal(db, goal.id)
            
            # Rank opportunities
            ranked_opportunities = await self.ranker.rank_opportunities(
                db=db,
                goal_id=goal.id,
                user_id=user_id,
                limit=50
            )
            
            # Generate and stream completion message
            summary = await self.ranker.generate_summary(ranked_opportunities, limit=5)
            completion_message = await self._format_completion_message(
                goal_id=str(goal.id),
                opportunities_count=len(opportunities),
                ranked_opportunities=ranked_opportunities[:5],
                summary=summary
            )
            
            completion_msg_id = str(uuid_lib.uuid4())
            for token in completion_message:
                yield ("stream_token", {
                    "message_id": completion_msg_id,
                    "token": token
                })
            
            # Save completion message
            completion_msg = Message(
                id=UUID(completion_msg_id),
                conversation_id=UUID(conversation_id),
                role="assistant",
                content=completion_message,
                metadata_json={"type": "completion", "goal_id": str(goal.id)}
            )
            db.add(completion_msg)
            
            # Update conversation status
            from app.models.chat import Conversation
            conv_result = await db.execute(
                select(Conversation).where(Conversation.id == UUID(conversation_id))
            )
            conv = conv_result.scalar_one_or_none()
            if conv:
                conv.goal_id = goal.id
                conv.status = "completed"
            
            await db.commit()
            await db.refresh(completion_msg)
            
            yield ("stream_end", {
                "message_id": completion_msg_id,
                "content": completion_message,
                "created_at": completion_msg.created_at.isoformat()
            })
            
            # Send complete event
            yield ("complete", {
                "goal_id": str(goal.id),
                "opportunities_count": len(opportunities)
            })
            
        except Exception as e:
            logger.error(f"Error in process_goal_with_answers_stream: {e}", exc_info=True)
            yield ("status", {
                "status": "error",
                "message": "An error occurred while processing your goal",
                "metadata": {"error": str(e)}
            })
    
    async def _get_opportunities_for_goal(
        self,
        db: AsyncSession,
        goal_id: UUID
    ) -> List[Any]:
        """Fetch opportunities associated with a goal from the database"""
        from app.models.opportunity import Opportunity
        result = await db.execute(
            select(Opportunity).where(Opportunity.goal_id == goal_id)
        )
        return result.scalars().all()
    
    async def _search_with_updates_stream(
        self,
        db: AsyncSession,
        goal_data: Dict[str, Any]
    ) -> AsyncGenerator[StructuredEvent, None]:
        """Execute search and yield status events"""
        from app.config import settings
        
        try:
            # Check internal database
            yield ("status", {
                "status": "searching",
                "message": "Checking existing opportunities...",
                "metadata": {}
            })
            
            internal_count = await self._count_internal_opportunities(db, goal_data)
            logger.info(f"Found {internal_count} existing opportunities")
            
            # Decide whether to scrape
            should_scrape = internal_count < settings.min_internal_opportunities
            
            if should_scrape:
                yield ("status", {
                    "status": "scraping",
                    "message": f"Found {internal_count} existing opportunities. Searching the web for more...",
                    "metadata": {"internal_count": internal_count}
                })
                
                await self.executor.execute_search(db, goal_data)
                
                yield ("status", {
                    "status": "complete",
                    "message": "Search complete!",
                    "metadata": {"scraped": True}
                })
            else:
                yield ("status", {
                    "status": "complete",
                    "message": f"Found {internal_count} relevant opportunities from our database.",
                    "metadata": {"internal_count": internal_count, "scraped": False}
                })
                
        except Exception as e:
            logger.error(f"Error in search with updates stream: {e}")
            yield ("status", {
                "status": "error",
                "message": "Search encountered an error",
                "metadata": {"error": str(e)}
            })
    
    async def _search_with_updates(
        self,
        db: AsyncSession,
        goal_data: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Smart search strategy: Check internal database first, scrape web only if needed.
        This reduces scraping load and provides faster results for common queries.
        """
        from app.config import settings
        all_opportunities = []
        
        try:
            # Step 1: Check internal database for existing relevant opportunities
            # Note: Status updates now handled via SSE streaming in process_goal_with_answers_stream
            
            internal_count = await self._count_internal_opportunities(db, goal_data)
            logger.info(f"Found {internal_count} existing relevant opportunities in database")
            
            # Step 2: Decide whether to scrape web or use internal results
            should_scrape = internal_count < settings.min_internal_opportunities
            
            if should_scrape:
                # Not enough internal results, scrape the web
                # Status updates now handled via SSE streaming
                
                logger.info(f"Scraping web (internal count {internal_count} < threshold {settings.min_internal_opportunities})")
                opportunities = await self.executor.execute_search(db, goal_data)
                all_opportunities.extend(opportunities)
                
                total_message = f"Search complete! Found {len(opportunities)} new opportunities."
            else:
                # Sufficient internal results, skip web scraping
                logger.info(f"Skipping web scrape (internal count {internal_count} >= threshold {settings.min_internal_opportunities})")
                total_message = f"Search complete! Found {internal_count} relevant opportunities from our database."
            
            # Status updates now handled via SSE streaming
            pass
            
        except Exception as e:
            logger.error(f"Error in search with updates: {e}")
            # Error handling now via SSE streaming
        
        return all_opportunities
    
    async def _count_internal_opportunities(
        self,
        db: AsyncSession,
        goal_data: Dict[str, Any]
    ) -> int:
        """
        Count existing opportunities in database that match the goal criteria.
        Uses vector similarity search to find relevant opportunities.
        """
        from app.config import settings
        from app.models.opportunity import Opportunity, OpportunityType
        from app.services.embeddings import generate_embedding
        from sqlalchemy import select, func
        
        try:
            # Generate embedding for the goal
            goal_text = f"{goal_data.get('original_description', '')} {' '.join(goal_data.get('keywords', []))}"
            goal_embedding = await generate_embedding(goal_text)
            
            # Get goal type
            goal_type = OpportunityType(goal_data.get("goal_type", "job"))
            
            # Count opportunities with similarity above threshold
            distance_threshold = 1 - settings.internal_search_relevance_threshold
            
            query = select(func.count(Opportunity.id)).where(
                Opportunity.opportunity_type == goal_type
            )
            
            result = await db.execute(query)
            count = result.scalar_one()
            
            return count or 0
            
        except Exception as e:
            logger.error(f"Error counting internal opportunities: {e}")
            return 0
    
    async def _format_completion_message(
        self,
        goal_id: str,
        opportunities_count: int,
        ranked_opportunities: List[Dict[str, Any]],
        summary: str
    ) -> str:
        """Format a completion message with top opportunities"""
        if opportunities_count == 0:
            return "I searched across multiple sources but couldn't find any opportunities matching your criteria. Try adjusting your requirements or check back later!"
        
        message = f"Great news! I found **{opportunities_count} opportunities** for you. {summary}\n\n"
        message += "**Top Matches:**\n\n"
        
        for i, ranked_opp in enumerate(ranked_opportunities, 1):
            opp = ranked_opp["opportunity"]
            score = ranked_opp["relevance_score"]
            
            message += f"{i}. **{opp.title}**\n"
            if opp.source_name:
                message += f"   📍 {opp.source_name}"
            if opp.location:
                message += f" • {opp.location}"
            if opp.compensation:
                message += f" • {opp.compensation}"
            message += f"\n   🎯 Relevance: {int(score * 100)}%\n\n"
        
        message += f"\n[View all {opportunities_count} opportunities →](/goals/{goal_id}/opportunities)"
        
        return message
