from typing import Dict, Any, List
from app.services.llm import structured_completion, chat_completion
from app.services.embeddings import generate_embedding
import logging

logger = logging.getLogger(__name__)


class ClarifierAgent:
    
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

