import openai
import json
from typing import List, Dict, Any, Optional, Generator, AsyncGenerator
import asyncio
import re

from ..config import CHAT_MODEL, OPENAI_API_KEY
from .prompt import SYSTEM_PROMPT, create_follow_up_prompt


# Set OpenAI API key
openai.api_key = OPENAI_API_KEY


async def generate_response_streaming(
    messages: list[dict],
    model: str = CHAT_MODEL
) -> AsyncGenerator[str, None]:
    """
    실시간 Streaming 구현
    """
    if messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    res = await openai.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    async for chunk in res:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content



def generate_response(
        messages: list[dict], 
        model: str = CHAT_MODEL
        ) -> str:
    """
    OpenAI 응답 생성
    """
    if messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

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
) -> list[str]:
    """
    후속 질문 생성 모듈
    """
    prompt = create_follow_up_prompt(question, answer, n)

    messages = [
        {"role": "system", "content": "You are a helpful QnA assistant that generates follow-up questions in Korean."},
        {"role": "user", "content": prompt}
    ]

    try:
        res = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=150,
            top_p=0.95
        )
        content = res.choices[0].message.content.strip()

        if not content.startswith("["):
            match = re.search(r"\[.*\]", content, re.DOTALL)
            content = match.group(0) if match else f'["{content}"]'

        follow_ups = json.loads(content)
        
        formatted_follow_ups = []
        for q in follow_ups:
            if not q.endswith("?") and not q.endswith("까?") and not q.endswith("요?"):
                q += "?"
            formatted_follow_ups.append(q)
            
        return formatted_follow_ups[:n]

    except Exception as e:
        print(f"후속 질문 생성 실패: {e}")
        return [
            "다른 정보가 필요하신가요?",
            "추가로 궁금한 점이 있으신가요?"
        ]