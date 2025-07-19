"""Prompt templates for LLM interactions."""

from typing import List, Dict, Any


# System prompt for the chatbot
SYSTEM_PROMPT = """
당신은 네이버 스마트스토어 FAQ를 기반으로 하는 챗봇입니다.
스마트스토어 관련 질문에 정확하고 친절하게 답변해 주세요.
스마트스토어와 관련 없는 질문에는 답변하지 말고, 스마트스토어 관련 질문을 해달라고 안내해 주세요.
답변은 간결하고 명확하게 제공하되, 필요한 정보를 모두 포함해야 합니다.
답변 끝에는 추가 질문이나 도움이 필요한지 물어보세요.
"""


def create_qa_prompt(question: str, retrieved_docs: List[Dict[str, Any]]) -> str:
    """
    Create a prompt for question answering.
    
    Args:
        question: User's question.
        retrieved_docs: Retrieved documents from the vector database.
        
    Returns:
        Prompt for the LLM.
    """
    prompt = f"질문: {question}\n\n"
    prompt += "다음은 관련 FAQ 정보입니다:\n\n"
    
    for i, doc in enumerate(retrieved_docs, 1):
        prompt += f"[FAQ {i}]\n"
        prompt += f"질문: {doc['question']}\n"
        prompt += f"답변: {doc['answer']}\n\n"
    
    prompt += "위 FAQ 정보를 바탕으로 질문에 답변해 주세요. 관련 정보가 없다면 솔직하게 모른다고 말하고, 스마트스토어 고객센터에 문의하라고 안내해 주세요."
    
    return prompt


def create_out_of_domain_response() -> str:
    """
    Create a response for out-of-domain questions.
    
    Returns:
        Response for out-of-domain questions.
    """
    return """
죄송합니다. 저는 네이버 스마트스토어 FAQ 챗봇으로, 스마트스토어 관련 질문에만 답변할 수 있습니다.
스마트스토어 이용, 판매자 등록, 상품 등록, 배송, 결제, 정산 등에 관한 질문을 해주시면 도움드리겠습니다.
    """


def create_follow_up_prompt(question: str, answer: str) -> str:
    """
    Create a prompt for generating follow-up questions.
    
    Args:
        question: User's question.
        answer: Answer to the user's question.
        
    Returns:
        Prompt for generating follow-up questions.
    """
    return f"""
사용자 질문: {question}
답변: {answer}

위 대화를 바탕으로 사용자가 추가로 물어볼 만한 자연스러운 후속 질문 2개를 생성해 주세요.
질문은 스마트스토어와 관련된 내용이어야 하며, 답변에서 언급된 주제와 연관성이 있어야 합니다.
질문 형식은 "~에 대해 더 알고 싶으신가요?" 또는 "~는 어떻게 하나요?" 등으로 해주세요.
""" 