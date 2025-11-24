from typing import Dict, Any, List, Optional, AsyncGenerator
from app.services.llm import structured_completion, chat_completion, chat_completion_stream
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
            structured_goal = await structured_completion(messages, model="gemini-2.5-flash")
            structured_goal["original_description"] = initial_description
            return structured_goal
        except Exception as e:
            logger.error(f"Error clarifying goal: {e}")
            raise
    
    async def generate_clarifying_questions(
        self, 
        initial_description: str, 
        preliminary_analysis: Dict[str, Any]
    ) -> str:
        """Generate a conversational message with clarifying questions"""
        prompt = f"""Based on this user goal: "{initial_description}"
        
        And this preliminary analysis:
        {preliminary_analysis}
        
        Write a friendly, conversational message asking 2-5 clarifying questions to better understand what they're looking for.
        
        Make it feel natural like you're chatting with someone, not like a form. Number your questions (1., 2., 3.) for clarity. For example:
        "I'd love to help you find the perfect opportunities! To narrow things down, could you tell me a bit more about:
        
        1. What specific technologies or areas are you most interested in?
        2. Are you looking for remote positions, or do you have a location preference?
        3. What's your ideal company size or type?"
        
        Keep it warm and conversational. Number the questions clearly. Just return the message text, no JSON."""
        
        messages = [
            {"role": "system", "content": "You are a friendly AI assistant helping someone find opportunities. You ask clarifying questions in a natural, conversational way."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await chat_completion(messages, model="gemini-2.5-flash", temperature=0.8)
            return response
        except Exception as e:
            logger.error(f"Error generating clarifying questions: {e}")
            return "I'd love to help you find the right opportunities! Could you tell me a bit more about what you're looking for?"
    
    async def generate_clarifying_questions_stream(
        self, 
        initial_description: str, 
        preliminary_analysis: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Stream a conversational message with clarifying questions"""
        prompt = f"""Based on this user goal: "{initial_description}"
        
        And this preliminary analysis:
        {preliminary_analysis}
        
        Write a brief, friendly intro followed by 2-3 numbered clarifying questions to better understand what they're looking for.
        
        Format example:
        "I'd love to help you find the perfect opportunities! To narrow things down:
        
        1. What specific technologies or areas are you most interested in?
        2. Are you looking for remote positions, or do you have a location preference?
        3. What's your ideal company size or type?"
        
        CRITICAL RULES:
        - End IMMEDIATELY after the last question
        - Do NOT add closing phrases like "Looking forward to...", "Let me know...", "Thanks!", or "Can't wait..."
        - Just: brief intro + 2-3 numbered questions
        - No pleasantries at the end"""
        
        messages = [
            {"role": "system", "content": "You are a friendly AI assistant helping someone find opportunities. You ask clarifying questions in a natural, conversational way."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            async for token in chat_completion_stream(messages, model="gemini-2.5-flash", temperature=0.8):
                yield token
        except Exception as e:
            logger.error(f"Error generating clarifying questions stream: {e}")
            yield "I'd love to help you find the right opportunities! Could you tell me a bit more about what you're looking for?"
    
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
            refined_goal = await structured_completion(messages, model="gpt-4o-mini")
            return refined_goal
        except Exception as e:
            logger.error(f"Error refining goal: {e}")
            return initial_goal
    
    def classify_intent(self, text: str) -> str:
        """
        Lightweight rule-based intent classification to route user turns:
        - 'meta' for UX/config feedback
        - 'greeting' for salutations
        - 'cancel' for cancellations
        - 'goal' for likely goal statements
        - 'unknown' fallback
        """
        t = (text or "").strip().lower()
        if not t:
            return "unknown"
        # Meta / UX feedback heuristics
        meta_markers = [
            "don't show", "dont show", "no thinking", "thinking indicator", "loading indicator",
            "ui", "ux", "interface", "cursor color", "auto focus", "autofocus", "layout", "design"
        ]
        if any(k in t for k in meta_markers):
            return "meta"
        # Greetings
        if t in {"hi", "hello", "hey", "hey there", "yo"} or t.startswith(("hi ", "hello ", "hey ")):
            return "greeting"
        # Cancel / stop
        if any(k in t for k in ["stop", "cancel", "never mind", "nevermind", "forget it"]):
            return "cancel"
        # Likely a goal if contains opportunity terms
        if any(k in t for k in ["job", "role", "position", "speaking", "conference", "event", "grant", "opportunity"]):
            return "goal"
        return "unknown"
    
    def is_goal_complete(self, goal: Dict[str, Any]) -> bool:
        """
        Check if the refined goal has the minimum fields to run a useful search.
        """
        if not goal:
            return False
        goal_type = (goal.get("goal_type") or "").strip()
        keywords = goal.get("keywords") or []
        location = (goal.get("location") or "").strip()
        # Require: goal_type and at least one of keywords/location/remote specified
        if goal_type not in {"job", "speaking", "grant", "event"}:
            return False
        has_keywords = isinstance(keywords, list) and len([k for k in keywords if str(k).strip()]) >= 1
        has_location = bool(location) or bool(goal.get("remote") is True)
        return has_keywords or has_location
    
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
    
    async def generate_next_question(
        self,
        collected_info: Dict[str, Any],
        asked_fields: List[str]
    ) -> Optional[str]:
        """Generate the next single clarifying question based on what's missing"""
        required = ["goal_type", "keywords", "location"]
        missing = [f for f in required if not collected_info.get(f) and f not in asked_fields]
        
        if not missing:
            return None
        
        next_field = missing[0]
        
        prompts = {
            "goal_type": "What type of opportunities are you looking for—speaking engagements, jobs, grants, or events?",
            "keywords": "What specific topics or technologies are you interested in?",
            "location": "Are you open to remote opportunities, or do you prefer a specific location?"
        }
        
        return prompts.get(next_field, "Could you tell me more about what you're looking for?")
    
    async def extract_partial_info(
        self,
        user_text: str,
        context: str,
        collected_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract any new info from user's response, even if incomplete"""
        prompt = f"""Previous context: {context}

Collected so far: {collected_info}

User's latest message: "{user_text}"

Extract ANY new information about:
- goal_type (speaking/job/grant/event)
- keywords/topics (array of strings)
- location (string) or remote (boolean)
- experience_level (string)

Return JSON with ONLY the NEW fields found. If nothing new, return empty dict {{}}.
Do not repeat already-collected fields."""
        
        messages = [
            {"role": "system", "content": "You extract structured information from conversational text."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            extracted = await structured_completion(messages, model="gpt-4o-mini")
            updated = {**collected_info, **extracted}
            return updated
        except Exception as e:
            logger.error(f"Error extracting partial info: {e}")
            return collected_info
    
    async def generate_confirmation_summary(self, goal_data: Dict[str, Any]) -> str:
        """Generate a confirmation summary before starting search"""
        goal_type = goal_data.get("goal_type", "opportunities")
        keywords = goal_data.get("keywords", [])
        location = goal_data.get("location", "any location")
        remote = goal_data.get("remote", False)
        
        summary = f"Got it! Looking for {goal_type}"
        
        if keywords:
            summary += f" in {', '.join(keywords[:3])}"
        
        if remote:
            summary += " (remote)"
        elif location and location.lower() not in ["any", "remote", ""]:
            summary += f" in {location}"
        
        summary += ". Starting search now..."
        return summary

