import asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator
import json

from ..memory.conversation import ConversationManager
from ..retrieval.vector_db import VectorDB
from ..retrieval.retriever import FAQRetriever
from ..embedding.vectorizer import get_embedding
from ..generation.llm import generate_response, generate_response_streaming, generate_follow_up_questions
from ..generation.prompt import create_qa_prompt, create_out_of_domain_response

router = APIRouter()

conversation_manager = ConversationManager()
vector_db = VectorDB()
retriever = FAQRetriever(vector_db)
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    question: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    follow_up_questions: List[str]


# Dependency to get or create session ID
def get_session_id(request: ChatRequest) -> str:
    """
    세션 ID 생성
    """
    if request.session_id:
        return request.session_id
    return str(uuid.uuid4())


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session_id: str = Depends(get_session_id)):
    """
    Chat endpoint
    """
    question = request.question
    
    is_domain_question = retriever.is_domain_question(question)
    
    if not is_domain_question:

        answer = create_out_of_domain_response()
        follow_up_questions = [
            "스마트스토어 판매자 등록에 대해 알고 싶으신가요?",
            "스마트스토어 상품 등록 방법이 궁금하신가요?"
        ]
    else:

        retrieved_docs = retriever.retrieve(question)
        
        conversation_context = conversation_manager.get_context_for_llm(session_id)
        
        prompt = create_qa_prompt(question, retrieved_docs)
        
        messages = conversation_context + [{"role": "user", "content": prompt}]
        
        answer = generate_response(messages)
        
        follow_up_questions = generate_follow_up_questions(question, answer)
    
    conversation_manager.add_message(session_id, "user", question)
    conversation_manager.add_message(session_id, "assistant", answer)
    
    return ChatResponse(
        session_id=session_id,
        answer=answer,
        follow_up_questions=follow_up_questions
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, session_id: str = Depends(get_session_id)):
    """
    스트리밍 채팅 API
    """
    question = request.question
    
    is_domain_question = retriever.is_domain_question(question)
    
    if not is_domain_question:
        answer = create_out_of_domain_response()
        
        conversation_manager.add_message(session_id, "user", question)
        conversation_manager.add_message(session_id, "assistant", answer)
        
        async def stream_out_of_domain():
            for chunk in answer.split():
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.05)
            
            follow_up_questions = [
                "스마트스토어 판매자 등록에 대해 알고 싶으신가요?",
                "스마트스토어 상품 등록 방법이 궁금하신가요?"
            ]
            follow_up_json = {"follow_up_questions": follow_up_questions}
            yield f"data: {json.dumps(follow_up_json)}\n\n"
            
            yield f"data: [DONE]\n\n"
        
        return StreamingResponse(stream_out_of_domain(), media_type="text/event-stream")
    
    retrieved_docs = retriever.retrieve(question)
    
    conversation_context = conversation_manager.get_context_for_llm(session_id)
    
    prompt = create_qa_prompt(question, retrieved_docs)
    
    messages = conversation_context + [{"role": "user", "content": prompt}]
    
    conversation_manager.add_message(session_id, "user", question)
    
    async def stream_response():
        full_response = ""
        
        async for chunk in generate_response_streaming(messages):
            full_response += chunk
            yield f"data: {chunk}\n\n"
        
        conversation_manager.add_message(session_id, "assistant", full_response)
        
        try:
            follow_up_questions = generate_follow_up_questions(question, full_response)
            
            follow_up_json = {"follow_up_questions": follow_up_questions}
            yield f"data: {json.dumps(follow_up_json)}\n\n"
        except Exception as e:
            print(f"후속 질문 생성 실패: {e}")
            default_follow_ups = ["다른 질문이 있으신가요?", "추가 정보가 필요하신가요?"]
            follow_up_json = {"follow_up_questions": default_follow_ups}
            yield f"data: {json.dumps(follow_up_json)}\n\n"
        
        yield f"data: [DONE]\n\n"
    
    return StreamingResponse(stream_response(), media_type="text/event-stream")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    session_id: Session ID
    """
    return conversation_manager.get_history(session_id)


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    session_id: Session ID
    """
    conversation_manager.clear_conversation(session_id)
    return {"message": "Chat history cleared"} 