from typing import Dict, Any, List, Optional
from app.services.llm import structured_completion, chat_completion
from app.services.embeddings import generate_embedding
import logging

logger = logging.getLogger(__name__)


class ClarifierAgent:
    """
    User-facing agent that handles all communication with the user.
    All user inputs come through this agent, and all outputs to the user
    are formatted and delivered by this agent.
    """
    
    async def clarify_goal(self, initial_description: str) -> Dict[str, Any]:
        system_prompt = """You are a goal clarification assistant. Your job is to understand user goals 
        and extract structured information about what they're looking for.
        
        Extract:
        - goal_type: one of "speaking", "job", "grant", "event"
        - keywords: list of relevant keywords
        - location: geographic preference (or "remote" or "any")
        - compensation_required: boolean
        - additional_filters: any other relevant criteria
        
        Return your response as JSON."""
        
        user_prompt = f"""User goal: "{initial_description}"
        
        Analyze this goal and return structured information in JSON format with these fields:
        - goal_type (speaking/job/grant/event)
        - keywords (array of strings)
        - location (string)
        - remote (boolean)
        - compensation_required (boolean)
        - timeframe (string, e.g., "immediate", "next 3 months", "ongoing")
        - experience_level (string, if applicable)
        - additional_filters (object with any other relevant info)
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            structured_goal = await structured_completion(messages, model="gpt-4")
            structured_goal["original_description"] = initial_description
            return structured_goal
        except Exception as e:
            logger.error(f"Error clarifying goal: {e}")
            raise
    
    async def generate_clarifying_questions(
        self, 
        initial_description: str, 
        preliminary_analysis: Dict[str, Any]
    ) -> List[str]:
        prompt = f"""Based on this user goal: "{initial_description}"
        
        And this preliminary analysis:
        {preliminary_analysis}
        
        Generate 2-3 clarifying questions to better understand what the user is looking for.
        Make questions specific and actionable. Return as a JSON array of strings."""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that asks clarifying questions."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await structured_completion(messages, model="gpt-4")
            return response.get("questions", [])
        except Exception as e:
            logger.error(f"Error generating clarifying questions: {e}")
            return []
    
    async def refine_goal_with_answers(
        self,
        initial_goal: Dict[str, Any],
        qa_pairs: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        qa_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs])
        
        prompt = f"""Initial goal analysis:
        {initial_goal}
        
        Additional Q&A:
        {qa_text}
        
        Update and refine the goal structure based on the new information.
        Return the updated goal as JSON with the same structure."""
        
        messages = [
            {"role": "system", "content": "You refine goal structures based on user answers."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            refined_goal = await structured_completion(messages, model="gpt-4")
            return refined_goal
        except Exception as e:
            logger.error(f"Error refining goal: {e}")
            return initial_goal
    
    async def generate_goal_embedding(self, goal_data: Dict[str, Any]) -> List[float]:
        embedding_text = f"""{goal_data.get('original_description', '')}
        Type: {goal_data.get('goal_type', '')}
        Keywords: {', '.join(goal_data.get('keywords', []))}
        Location: {goal_data.get('location', '')}
        """
        
        return await generate_embedding(embedding_text.strip())
    
    async def format_results_for_user(
        self,
        opportunities_count: int,
        summary: Optional[str] = None,
        status: str = "completed"
    ) -> str:
        """
        Format search results into a user-friendly message.
        All communication to the user goes through this method.
        """
        if status == "processing":
            return "I'm searching for opportunities that match your goal. This may take 30-60 seconds..."
        
        if status == "error":
            return "I encountered an issue while searching. Please try again or refine your goal."
        
        if opportunities_count == 0:
            return """I couldn't find any opportunities matching your criteria right now. 
            
            Try:
            - Broadening your search terms
            - Removing location restrictions
            - Trying a different opportunity type
            
            I'll keep monitoring for new opportunities!"""
        
        base_message = f"Great news! I found {opportunities_count} opportunities for you."
        
        if summary:
            return f"{base_message}\n\n{summary}\n\nYou can now browse the results and provide feedback to help me improve future searches!"
        
        return f"{base_message}\n\nYou can now browse the results and provide feedback!"
    
    async def acknowledge_feedback(self, rating: int) -> str:
        """
        Acknowledge user feedback in a friendly way.
        """
        if rating >= 4:
            return "Thanks for the feedback! I'll prioritize similar opportunities in the future."
        elif rating <= 2:
            return "Thanks for letting me know. I'll adjust my search to find better matches."
        else:
            return "Thanks for your feedback!"
    
    async def explain_goal_clarification(self, structured_goal: Dict[str, Any]) -> str:
        """
        Explain to the user how their goal was interpreted.
        """
        goal_type = structured_goal.get('goal_type', 'opportunity')
        keywords = structured_goal.get('keywords', [])
        location = structured_goal.get('location', 'any location')
        
        message = f"""I understand you're looking for {goal_type} opportunities"""
        
        if keywords:
            message += f" related to {', '.join(keywords[:3])}"
        
        if location and location.lower() not in ['any', 'remote', '']:
            message += f" in {location}"
        elif structured_goal.get('remote', False):
            message += " (remote positions)"
        
        message += ".\n\nI'll search across multiple platforms and notify you when I find relevant opportunities."
        
        return message

