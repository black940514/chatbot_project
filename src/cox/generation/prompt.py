from typing import List, Dict, Any


# System prompt for the chatbot
SYSTEM_PROMPT = """
당신은 네이버 스마트스토어 FAQ를 기반으로 하는 챗봇입니다.
스마트스토어 관련 질문에 정확하고 친절하게 답변해 주세요.
스마트스토어와 관련 없는 질문에는 답변하지 말고, 스마트스토어 관련 질문을 해달라고 안내해 주세요.
답변은 간결하고 명확하게 제공하되, 필요한 정보를 모두 포함해야 합니다.
답변 끝에는 추가 질문이나 도움이 필요한지 물어보세요.
"""


def create_qa_prompt(question: str, retrieved_docs: list[dict]) -> str:
    """
    Q&A 프롬프트 생성
    """
    prompt = f"질문: {question}\n\n"
    prompt += "다음은 관련 FAQ 정보입니다:\n\n"

    for i, doc in enumerate(retrieved_docs, 1):
        prompt += f"[FAQ {i}]\n"
        prompt += f"질문: {doc['question']}\n"
        prompt += f"답변: {doc['answer']}\n\n"

    prompt += "위 FAQ 정보를 참고해서 질문에 답해주세요. 관련 내용이 없으면 모른다고 말하고 스마트스토어 고객센터를 안내해 주세요."
    return prompt



def create_out_of_domain_response() -> str:
    """
    스마트스토어와 관련 없는 질문에는 답변 X
    -> fallback 응답
    """
    return """죄송합니다. 저는 스마트 스토어 FAQ를 위한 챗봇입니다. 스마트 스토어에 대한 질문을 부탁드립니다.
예를 들어 아래와 같은 질문은 도와드릴 수 있어요:
- 스마트스토어 판매자 등록 절차는?
- 배송비는 누가 부담하나요?"""


def create_follow_up_prompt(question: str, answer: str) -> str:
    """
    후속 질문 생성 프롬프트
    """
    return f"""
사용자 질문: {question}
답변: {answer}

위 대화를 바탕으로 사용자가 추가로 물어볼 만한 자연스러운 후속 질문 2개를 생성해 주세요.
질문은 스마트스토어와 관련된 내용이어야 하며, 답변에서 언급된 주제와 연관성이 있어야 합니다.
질문 형식은 "~에 대해 더 알고 싶으신가요?" 또는 "~는 어떻게 하나요?" 등으로 해주세요.
""" 