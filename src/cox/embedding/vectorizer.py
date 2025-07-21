import openai
import numpy as np
from typing import Dict, Any, List, Union

from ..config import EMBEDDING_MODEL, OPENAI_API_KEY


# Set OpenAI API key
openai.api_key = OPENAI_API_KEY


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    """
    openai api 임베딩 생성
    """
    try:
        res = openai.embeddings.create(model=model, input=text)
        return res.data[0].embedding
    except Exception as e:
        raise ValueError(f"임베딩 생성 실패: {e}")



def embed_chunked_qna(chunked_qna: dict, model: str = EMBEDDING_MODEL) -> dict:
    """
    청크 QnA pair 임베딩 생성
    """
    result = {}
    
    for chunk_id, data in chunked_qna.items():
        try:
            q_emb = get_embedding(data["question"], model)
            a_emb = get_embedding(data["answer"], model)
            result[chunk_id] = {
                **data,
                "question_embedding": q_emb,
                "answer_embedding": a_emb
            }
        except Exception as e:
            print(f"[{chunk_id}] 임베딩 실패: {e}")
            continue
    return result


def combine_embeddings(embeddings: list[list[float]]) -> list[float]:
    """
    임베딩 평균 조합
    -> 문장 단위 인인베딩 생성
    """
    if not embeddings:
        raise ValueError("빈 임베딩 리스트입니다.")
    return list(np.mean(embeddings, axis=0))