"""API router for the chat endpoint."""

import asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator

from ..memory.conversation import ConversationManager
from ..retrieval.vector_db import VectorDB
from ..retrieval.retriever import FAQRetriever
from ..embedding.vectorizer import get_embedding
from ..generation.llm import generate_response, generate_response_streaming, generate_follow_up_questions
from ..generation.prompt import create_qa_prompt, create_out_of_domain_response


# Create router
router = APIRouter()

# Create conversation manager
conversation_manager = ConversationManager()

# Create vector DB and retriever
vector_db = VectorDB()
retriever = FAQRetriever(vector_db)


# Request and response models
class ChatRequest(BaseModel):
    """Chat request model."""
    session_id: Optional[str] = None
    question: str


class ChatResponse(BaseModel):
    """Chat response model."""
    session_id: str
    answer: str
    follow_up_questions: List[str]


# Dependency to get or create session ID
def get_session_id(request: ChatRequest) -> str:
    """
    Get or create session ID.
    
    Args:
        request: Chat request.
        
    Returns:
        Session ID.
    """
    if request.session_id:
        return request.session_id
    return str(uuid.uuid4())


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session_id: str = Depends(get_session_id)):
    """
    Chat endpoint.
    
    Args:
        request: Chat request.
        session_id: Session ID.
        
    Returns:
        Chat response.
    """
    question = request.question
    
    # Check if the question is related to the domain
    is_domain_question = retriever.is_domain_question(question)
    
    if not is_domain_question:
        # Out of domain question
        answer = create_out_of_domain_response()
        follow_up_questions = [
            "스마트스토어 판매자 등록에 대해 알고 싶으신가요?",
            "스마트스토어 상품 등록 방법이 궁금하신가요?"
        ]
    else:
        # Retrieve relevant FAQ entries
        retrieved_docs = retriever.retrieve(question)
        
        # Get conversation context
        conversation_context = conversation_manager.get_context_for_llm(session_id)
        
        # Create prompt with retrieved documents
        prompt = create_qa_prompt(question, retrieved_docs)
        
        # Add prompt to messages
        messages = conversation_context + [{"role": "user", "content": prompt}]
        
        # Generate response
        answer = generate_response(messages)
        
        # Generate follow-up questions
        follow_up_questions = generate_follow_up_questions(question, answer)
    
    # Save conversation
    conversation_manager.add_message(session_id, "user", question)
    conversation_manager.add_message(session_id, "assistant", answer)
    
    # Return response
    return ChatResponse(
        session_id=session_id,
        answer=answer,
        follow_up_questions=follow_up_questions
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, session_id: str = Depends(get_session_id)):
    """
    Streaming chat endpoint.
    
    Args:
        request: Chat request.
        session_id: Session ID.
        
    Returns:
        Streaming response.
    """
    question = request.question
    
    # Check if the question is related to the domain
    is_domain_question = retriever.is_domain_question(question)
    
    if not is_domain_question:
        # Out of domain question
        answer = create_out_of_domain_response()
        
        # Save conversation
        conversation_manager.add_message(session_id, "user", question)
        conversation_manager.add_message(session_id, "assistant", answer)
        
        # Return streaming response
        async def stream_out_of_domain():
            for chunk in answer.split():
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.05)
            
            # End the stream
            yield f"data: [DONE]\n\n"
        
        return StreamingResponse(stream_out_of_domain(), media_type="text/event-stream")
    
    # Retrieve relevant FAQ entries
    retrieved_docs = retriever.retrieve(question)
    
    # Get conversation context
    conversation_context = conversation_manager.get_context_for_llm(session_id)
    
    # Create prompt with retrieved documents
    prompt = create_qa_prompt(question, retrieved_docs)
    
    # Add prompt to messages
    messages = conversation_context + [{"role": "user", "content": prompt}]
    
    # Save user message
    conversation_manager.add_message(session_id, "user", question)
    
    # Generate response with streaming
    async def stream_response():
        full_response = ""
        
        async for chunk in generate_response_streaming(messages):
            full_response += chunk
            yield f"data: {chunk}\n\n"
        
        # Save assistant message after generation is complete
        conversation_manager.add_message(session_id, "assistant", full_response)
        
        # End the stream
        yield f"data: [DONE]\n\n"
    
    return StreamingResponse(stream_response(), media_type="text/event-stream")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get chat history.
    
    Args:
        session_id: Session ID.
        
    Returns:
        Chat history.
    """
    return conversation_manager.get_history(session_id)


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history.
    
    Args:
        session_id: Session ID.
        
    Returns:
        Success message.
    """
    conversation_manager.clear_conversation(session_id)
    return {"message": "Chat history cleared"} 