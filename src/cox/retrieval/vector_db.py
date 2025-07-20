import os
from typing import Dict, List, Any, Optional, Union

import chromadb
from chromadb.config import Settings

from ..config import COLLECTION_NAME, VECTOR_DB_PATH


class VectorDB:
    """
    ChromaDB 클래스
    """

    def __init__(
        self,
        collection_name: str = COLLECTION_NAME,
        persist_directory: str = VECTOR_DB_PATH
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Using existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(name=collection_name)
            print(f"Created new collection: {collection_name}")

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        벡터 DB에 임베딩, 메타데이터 추가
        """
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Added {len(documents)} documents to collection {self.collection_name}")

    def add_faq_data(self, embedded_qna: Dict[int, Dict[str, Any]]) -> None:
        """
        FAQ 데이터 청크로 DB에 등록
        """
        ids = []
        docs = []
        embs = []
        metas = []

        for idx, chunk in embedded_qna.items():
            ids.append(f"faq_{idx}")
            docs.append(chunk["question"])
            embs.append(chunk["question_embedding"])
            metas.append({
                "answer": chunk["answer"],
                "original_question": chunk["original_question"]
            })

        self.add_documents(docs, embs, ids, metas)

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        벡터 DB에 질문 임베딩을 보내고 유사도 기반 결과 반환
        query_embedding: 검색할 문장 임베딩
        n_results: 가져올 문서 수
            {
              "documents": [[...]],
              "metadatas": [[...]],
              "distances": [[...]]
            }
        
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

    def delete_collection(self) -> None:
        """
        현재 컬렉션 전체 삭제
        """
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")

    def count(self) -> int:
        """
        컬렉션에 저장된 문서 총 개수 return
        """
        return self.collection.count()

    def get_collection_info(self) -> Dict[str, Any]:
        """
        컬렉션 이름과 문서 개수를 묶어서 return
        """
        return {
            "name": self.collection_name,
            "count": self.collection.count()
        }