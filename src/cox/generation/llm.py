"""LLM module for interacting with the OpenAI API."""

import openai
import json
from typing import List, Dict, Any, Optional, Generator, AsyncGenerator
import asyncio

from ..config import CHAT_MODEL, OPENAI_API_KEY
from .prompt import SYSTEM_PROMPT


# Set OpenAI API key
openai.api_key = OPENAI_API_KEY


async def generate_response_streaming(
    messages: List[Dict[str, str]],
    model: str = CHAT_MODEL
) -> AsyncGenerator[str, None]:
    """
    Generate a response from the LLM with streaming.
    
    Args:
        messages: List of messages in the conversation.
        model: Model to use for generation.
        
    Yields:
        Chunks of the generated response.
    """
    # Add system prompt if not present
    if messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    
    # Call the OpenAI API with streaming
    response = await openai.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    
    # Stream the response
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def generate_response(
    messages: List[Dict[str, str]],
    model: str = CHAT_MODEL
) -> str:
    """
    Generate a response from the LLM.
    
    Args:
        messages: List of messages in the conversation.
        model: Model to use for generation.
        
    Returns:
        Generated response.
    """
    # Add system prompt if not present
    if messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    
    # Call the OpenAI API
    response = openai.chat.completions.create(
        model=model,
        messages=messages
    )
    
    return response.choices[0].message.content


def generate_follow_up_questions(
    question: str,
    answer: str,
    n: int = 2,
    model: str = CHAT_MODEL
) -> List[str]:
    """
    Generate follow-up questions based on the question and answer.
    
    Args:
        question: Original question.
        answer: Answer to the question.
        n: Number of follow-up questions to generate.
        model: Model to use for generation.
        
    Returns:
        List of follow-up questions.
    """
    prompt = f"""
사용자 질문: {question}
답변: {answer}

위 대화를 바탕으로 사용자가 추가로 물어볼 만한 자연스러운 후속 질문 {n}개를 생성해 주세요.
질문은 스마트스토어와 관련된 내용이어야 하며, 답변에서 언급된 주제와 연관성이 있어야 합니다.
질문 형식은 "~에 대해 더 알고 싶으신가요?" 또는 "~는 어떻게 하나요?" 등으로 해주세요.
JSON 형식으로 반환해주세요: ["질문1", "질문2"]
"""
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates follow-up questions in Korean."},
        {"role": "user", "content": prompt}
    ]
    
    # Call the OpenAI API
    response = openai.chat.completions.create(
        model=model,
        messages=messages
    )
    
    # Parse the response as JSON
    try:
        content = response.choices[0].message.content
        # Extract JSON array from the response if it's not a pure JSON
        if not content.strip().startswith('['):
            import re
            json_match = re.search(r'\[(.*)\]', content, re.DOTALL)
            if json_match:
                content = f"[{json_match.group(1)}]"
            else:
                # Fallback to simple parsing
                return content.split('\n')[:n]
        
        questions = json.loads(content)
        return questions[:n]
    except Exception as e:
        print(f"Error parsing follow-up questions: {str(e)}")
        # Fallback to rule-based follow-up questions
        return [
            "추가로 다른 정보가 필요하신가요?",
            "다른 질문이 있으신가요?"
        ] 