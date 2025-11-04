from typing import Dict, Any, List, TypedDict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import logging
from langgraph.graph import StateGraph, END

from app.agents.clarifier import ClarifierAgent
from app.agents.executor import ExecutorAgent
from app.agents.ranker import RankerAgent
from app.services.ably_service import ably_service
from app.models.goal import Goal, GoalStatus, GoalType

logger = logging.getLogger(__name__)


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
    
    async def generate_questions(self, initial_description: str) -> List[Dict[str, str]]:
        """Generate clarifying questions for the initial goal description"""
        try:
            preliminary_analysis = await self.clarifier.clarify_goal(initial_description)
            questions = await self.clarifier.generate_clarifying_questions(
                initial_description, 
                preliminary_analysis
            )
            
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    "question": q,
                    "type": "text"
                })
            
            return formatted_questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return []
    
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
            refined_goal = await self.clarifier.refine_goal_with_answers(
                preliminary_goal,
                qa_pairs
            )
            
            goal_embedding = await self.clarifier.generate_goal_embedding(refined_goal)
            refined_goal["embedding"] = goal_embedding
            
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
                ably_service.publish_status(
                    conversation_id,
                    "searching",
                    "Starting opportunity search...",
                    {"goal_id": str(goal.id)}
                )
            
            opportunities = await self._search_with_updates(
                db, 
                refined_goal, 
                conversation_id
            )
            
            explanation = await self.clarifier.explain_goal_clarification(refined_goal)
            user_message = await self.clarifier.format_results_for_user(
                opportunities_count=len(opportunities),
                status="completed"
            )
            
            return {
                "success": True,
                "goal_id": str(goal.id),
                "clarified_goal": refined_goal,
                "opportunities_found": len(opportunities),
                "user_message": user_message,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Error processing goal with answers: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_message": "I encountered an error processing your goal. Please try again."
            }
    
    async def _search_with_updates(
        self,
        db: AsyncSession,
        goal_data: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute search and broadcast status updates via WebSocket"""
        all_opportunities = []
        
        try:
            opportunities = await self.executor.execute_search(db, goal_data)
            all_opportunities.extend(opportunities)
            
            if conversation_id:
                ably_service.publish_status(
                    conversation_id,
                    "complete",
                    f"Search complete! Found {len(opportunities)} opportunities.",
                    {"count": len(opportunities)}
                )
            
        except Exception as e:
            logger.error(f"Error in search with updates: {e}")
            if conversation_id:
                ably_service.publish_status(
                    conversation_id,
                    "error",
                    "Search encountered an error",
                    {"error": str(e)}
                )
        
        return all_opportunities
