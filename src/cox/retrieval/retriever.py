from typing import Dict, List, Any, Tuple, Optional

from ..config import DOMAIN_KEYWORDS
from ..embedding.vectorizer import get_embedding
from .vector_db import VectorDB


class FAQRetriever:
    """
    FAQ에서 유사한 항목을 찾아주는 역할
    """
    
    def __init__(self, vector_db: VectorDB):
        self.vector_db = vector_db 

    def retrieve(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        1) 사용자가 입력한 query를 임베딩으로 변환
        2) 벡터 DB에서 가장 유사한 FAQ 문서 {n_results}개 검색
        3) 결과를 {'question', 'answer', 'original_question', 'similarity'} 형태로 반환
        """
        # 1) 임베딩 생성
        query_embedding = get_embedding(query)

        # 2) 벡터 DB 질의
        results = self.vector_db.query(query_embedding, n_results)

        # 3) 결과 포맷
        formatted = []
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        
        for i in range(len(docs)):
            formatted.append({
                "question": docs[i],
                "answer": metas[i]["answer"],
                "original_question": metas[i]["original_question"],
                "similarity": 1 - dists[i] # 거리를 유사도로 변환
            })
        return formatted

    def is_domain_question(self, query: str, threshold: float = 0.1) -> bool:
        """
        유사 질문인지 판단하는 함수
        1) DOMAIN_KEYWORDS에 키워드 포함 여부 확인
        2) 키워드 없으면 retrieve로 유사도 확인
        """
        low = query.lower()
        # 1) 키워드 기반 필터
        for kw in DOMAIN_KEYWORDS:
            if kw.lower() in low:
                return True

        # 2) 벡터 유사도 필터링
        top = self.retrieve(query, n_results=1)
        if top and top[0]["similarity"] >= threshold:
            return True

        return False
