"""Retriever module for finding relevant FAQ entries."""

from typing import Dict, List, Any, Tuple, Optional

from ..config import DOMAIN_KEYWORDS
from ..embedding.vectorizer import get_embedding
from .vector_db import VectorDB


class FAQRetriever:
    """Retriever for FAQ entries."""
    
    def __init__(self, vector_db: VectorDB):
        """
        Initialize the retriever.
        
        Args:
            vector_db: Vector database instance.
        """
        self.vector_db = vector_db
    
    def retrieve(
        self, 
        query: str, 
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant FAQ entries.
        
        Args:
            query: Query text.
            n_results: Number of results to return.
            
        Returns:
            List of relevant FAQ entries.
        """
        # Get query embedding
        query_embedding = get_embedding(query)
        
        # Query the vector database
        results = self.vector_db.query(query_embedding, n_results)
        
        # Format the results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "question": results["documents"][0][i],
                "answer": results["metadatas"][0][i]["answer"],
                "original_question": results["metadatas"][0][i]["original_question"],
                "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    
    def is_domain_question(self, query: str, threshold: float = 0.1) -> bool:
        """
        Check if a query is related to the domain.
        
        Args:
            query: Query text.
            threshold: Minimum similarity threshold.
            
        Returns:
            True if the query is related to the domain, False otherwise.
        """
        # Simple keyword-based check
        query_lower = query.lower()
        for keyword in DOMAIN_KEYWORDS:
            if keyword.lower() in query_lower:
                return True
        
        # If no keywords match, use vector similarity
        results = self.retrieve(query, n_results=1)
        if results and results[0]["similarity"] >= threshold:
            return True
        
        return False
    
    def generate_follow_up_questions(
        self, 
        query: str, 
        answer: str, 
        n_questions: int = 2
    ) -> List[str]:
        """
        Generate follow-up questions based on the query and answer.
        
        Args:
            query: Original query.
            answer: Answer to the query.
            n_questions: Number of follow-up questions to generate.
            
        Returns:
            List of follow-up questions.
        """
        # For now, use a simple rule-based approach
        # In a real system, you might use an LLM to generate these
        
        # Extract keywords from the answer
        keywords = set()
        for keyword in DOMAIN_KEYWORDS:
            if keyword.lower() in answer.lower():
                keywords.add(keyword)
        
        # Generate follow-up questions based on keywords
        follow_ups = []
        
        if "등록" in keywords or "가입" in keywords:
            follow_ups.append("등록 절차에 대해 더 자세히 알고 싶으신가요?")
        
        if "서류" in keywords:
            follow_ups.append("필요한 서류 목록을 확인하고 싶으신가요?")
        
        if "비용" in keywords or "수수료" in keywords:
            follow_ups.append("관련 비용이나 수수료에 대해 더 알고 싶으신가요?")
        
        if "배송" in keywords:
            follow_ups.append("배송 정책에 대해 더 알고 싶으신가요?")
        
        if "환불" in keywords or "취소" in keywords or "반품" in keywords:
            follow_ups.append("환불/취소/반품 절차에 대해 더 알고 싶으신가요?")
        
        if "정산" in keywords:
            follow_ups.append("정산 주기나 방식에 대해 더 알고 싶으신가요?")
        
        # Default follow-up questions if we couldn't generate enough
        default_follow_ups = [
            "다른 질문이 있으신가요?",
            "스마트스토어 이용 중 다른 궁금한 점이 있으신가요?",
            "추가로 도움이 필요하신 부분이 있으신가요?",
            "다른 정보가 필요하신가요?"
        ]
        
        # Combine and limit to n_questions
        all_follow_ups = follow_ups + default_follow_ups
        return all_follow_ups[:n_questions] 