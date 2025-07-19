import re
from typing import Dict, Any, List, Tuple


def clean_text(text: str) -> str:
    """
    텍스트 전처리
    """
    text = re.sub(r'<.*?>', '', text)

    text = re.sub(r'[\xa0\u200b\u3000]', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()




def extract_qa_pairs(data: dict) -> dict:
    """
    질문-답변 pair 추출
    """
    qa_pairs = {}
    for q, a in data.items():
        q = clean_text(q)
        a = clean_text(a)
        if q and a:
            qa_pairs[q] = a
    return qa_pairs





def filter_qa_pairs(qa_pairs: dict, min_q_length: int = 5, min_a_length: int = 10) -> dict:
    """
    Q&A 데이터 전처리 
    -> 응답 품질 개선 및 벡터 검색 개선
    """
    result = {}
    for q, a in qa_pairs.items():
        if len(q) >= min_q_length and len(a) >= min_a_length:
            result[q] = a
    return result





def remove_faq_metadata(text: str) -> str:
    """
    Answer 도움말 제거 파싱용
    """
    text = re.sub(r'위 도움말이 도움이 되었나요\?.*?도움말 닫기', '', text, flags=re.DOTALL)
    text = re.sub(r'관련 도움말\/키워드.*?도움말 닫기', '', text, flags=re.DOTALL)
    return clean_text(text)


def preprocess_faq_data(data: dict) -> dict:
    """
    데이터 전처리 파이프라인
    """
    qa_pairs = extract_qa_pairs(data)
    qa_cleaned = {q: remove_faq_metadata(a) for q, a in qa_pairs.items()}
    return filter_qa_pairs(qa_cleaned)
