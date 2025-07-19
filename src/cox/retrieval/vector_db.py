"""Vector database module for managing the ChromaDB instance."""

import os
from typing import Dict, List, Any, Optional, Union

import chromadb
from chromadb.config import Settings

from ..config import COLLECTION_NAME, VECTOR_DB_PATH


class VectorDB:
    """Vector database manager for ChromaDB."""
    
    def __init__(
        self, 
        collection_name: str = COLLECTION_NAME, 
        persist_directory: str = VECTOR_DB_PATH
    ):
        """
        Initialize the vector database.
        
        Args:
            collection_name: Name of the collection to use.
            persist_directory: Directory to persist the database.
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Create the persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize the client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create the collection
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
        Add documents to the vector database.
        
        Args:
            documents: List of document texts.
            embeddings: List of document embeddings.
            ids: List of document IDs.
            metadatas: List of document metadata.
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
        Add FAQ data to the vector database.
        
        Args:
            embedded_qna: Dictionary of embedded QnA pairs.
        """
        id_list = []
        documents = []
        embeddings = []
        metadatas = []
        
        for idx, chunk in embedded_qna.items():
            id_list.append(f"faq_{idx}")
            documents.append(chunk["question"])
            embeddings.append(chunk["question_embedding"])
            metadatas.append({
                "answer": chunk["answer"],
                "original_question": chunk["original_question"]
            })
        
        self.add_documents(documents, embeddings, id_list, metadatas)
    
    def query(
        self, 
        query_embedding: List[float], 
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query the vector database.
        
        Args:
            query_embedding: Query embedding.
            n_results: Number of results to return.
            
        Returns:
            Dictionary containing query results.
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
    
    def delete_collection(self) -> None:
        """Delete the collection."""
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")
    
    def count(self) -> int:
        """
        Count the number of documents in the collection.
        
        Returns:
            Number of documents.
        """
        return self.collection.count()
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary containing collection information.
        """
        return {
            "name": self.collection_name,
            "count": self.collection.count()
        } 