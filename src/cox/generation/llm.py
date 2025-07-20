import openai
import json
from typing import List, Dict, Any, Optional, Generator, AsyncGenerator
import asyncio
import re

from ..config import CHAT_MODEL, OPENAI_API_KEY
from .prompt import SYSTEM_PROMPT


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
    prompt = f"""
사용자 질문: {question}
답변: {answer}

위 대화를 바탕으로 사용자가 궁금해할만한 다른 내용 {n}개를 만들어 주세요.
스마트스토어 관련 질문이어야 하며, 답변과 연관된 주제로 해 주세요.
형식: ["질문1", "질문2"]
"""

    messages = [
        {"role": "system", "content": "You are a helpful QnA assistant that generates follow-up questions in Korean."},
        {"role": "user", "content": prompt}
    ]

    try:
        res = openai.chat.completions.create(model=model, messages=messages)
        content = res.choices[0].message.content.strip()

        if not content.startswith("["):
            match = re.search(r"\[.*\]", content, re.DOTALL)
            content = match.group(0) if match else f'["{content}"]'

        return json.loads(content)[:n]

    except Exception as e:
        print(f"후속 질문 생성 실패: {e}")
        return ["다른 도움이 필요하신가요?", "더 궁금한 점이 있으신가요?"]