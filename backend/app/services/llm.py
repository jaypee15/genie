from openai import AsyncOpenAI
from typing import Dict, Any, List, Optional
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None
) -> str:
    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
            
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise


async def structured_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-4",
    temperature: float = 0.7
) -> Dict[str, Any]:
    try:
        response = await chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        return json.loads(response)
    except Exception as e:
        logger.error(f"Error in structured completion: {e}")
        raise


async def summarize_opportunities(opportunities: List[Dict[str, Any]]) -> str:
    prompt = f"""Summarize the following {len(opportunities)} opportunities in a brief, engaging way.
Focus on the most relevant and interesting aspects.

Opportunities:
{json.dumps(opportunities, indent=2)}

Provide a natural language summary that highlights:
1. The total number and types of opportunities
2. Key highlights or standout opportunities
3. Geographic distribution if relevant
"""
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes job and opportunity listings."},
        {"role": "user", "content": prompt}
    ]
    
    return await chat_completion(messages, model="gpt-4o-mini", max_tokens=300)

