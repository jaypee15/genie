from typing import Dict, Any, List, Optional, AsyncGenerator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)


def _build_chat_model(
    model: str,
    temperature: float,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None,
    streaming: bool = False,
) -> ChatGoogleGenerativeAI:
    model_kwargs: Dict[str, Any] = {}
    
    # Note: Gemini doesn't support response_format like OpenAI's JSON mode
    # Instead, we'll use system prompts to request JSON output
    if response_format and response_format.get("type") == "json_object":
        logger.warning("Gemini doesn't support native JSON mode - using prompt-based JSON formatting")

    return ChatGoogleGenerativeAI(
        google_api_key=settings.google_api_key,
        model=model,
        temperature=temperature,
        max_output_tokens=max_tokens,
        convert_system_message_to_human=True,  # Gemini requires system messages to be converted
    )


def _convert_messages(messages: List[Dict[str, str]]) -> List[BaseMessage]:
    converted: List[BaseMessage] = []
    for message in messages:
        role = (message.get("role") or "user").lower()
        content = message.get("content") or ""

        if role == "system":
            converted.append(SystemMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))
        else:
            converted.append(HumanMessage(content=content))

    return converted


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if part is None:
                continue
            if isinstance(part, dict):
                if part.get("type") == "text" and "text" in part:
                    parts.append(part["text"])
            else:
                parts.append(str(part))
        return "".join(parts)
    return ""


def _extract_chunk_text(chunk: AIMessageChunk) -> str:
    return _content_to_text(chunk.content)


async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gemini-1.5-flash",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None
) -> str:
    try:
        chat = _build_chat_model(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )
        lc_messages = _convert_messages(messages)
        response = await chat.ainvoke(lc_messages)
        return _content_to_text(response.content)
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise


async def structured_completion(
    messages: List[Dict[str, str]],
    model: str = "gemini-1.5-flash",
    temperature: float = 0.7
) -> Dict[str, Any]:
    try:
        # Gemini doesn't have native JSON mode, so we add instructions to the prompt
        # Ensure the last user message requests JSON format
        enhanced_messages = messages.copy()
        if enhanced_messages and enhanced_messages[-1].get("role") == "user":
            original_content = enhanced_messages[-1]["content"]
            enhanced_messages[-1]["content"] = f"{original_content}\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown, no explanations, just the JSON object."
        
        response = await chat_completion(
            messages=enhanced_messages,
            model=model,
            temperature=temperature,
            response_format=None  # Gemini doesn't support this parameter
        )
        
        # Clean up response - sometimes Gemini adds markdown code blocks
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        return json.loads(cleaned_response)
    except Exception as e:
        logger.error(f"Error in structured completion: {e}")
        logger.error(f"Response was: {response if 'response' in locals() else 'N/A'}")
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
    
    return await chat_completion(messages, model="gemini-1.5-flash", max_tokens=300)


async def chat_completion_stream(
    messages: List[Dict[str, str]],
    model: str = "gemini-1.5-flash",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """Stream chat completion tokens as they are generated"""
    try:
        chat = _build_chat_model(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
        lc_messages = _convert_messages(messages)

        async for chunk in chat.astream(lc_messages):
            token = _extract_chunk_text(chunk)
            if token:
                yield token
                
    except Exception as e:
        logger.error(f"Error in streaming chat completion: {e}")
        raise

