import argparse

from cox.data.loader import load_faq_data
from cox.embedding.chunker import process_qna_dict
from cox.embedding.vectorizer import embed_chunked_qna
from cox.retrieval.vector_db import VectorDB
from cox.api.app import run_app


def load_and_index_data(data_path: str = None, rebuild_index: bool = False):
    """
    데이터 로드 및 벡터 인덱스 생성
    """
    
    print("Loading FAQ data...")
    faq_data = load_faq_data(data_path)
    
    # Create vector DB
    vector_db = VectorDB()
    
    # Check if we need to rebuild the index
    if rebuild_index or vector_db.count() == 0:
        print("Building vector index...")
        
        # Process and embed the FAQ data
        if "question_embedding" not in list(faq_data.values())[0]:
            print("Processing and embedding FAQ data...")
            chunked_data = process_qna_dict(faq_data)
            embedded_data = embed_chunked_qna(chunked_data)
        else:
            print("Using pre-embedded FAQ data...")
            embedded_data = faq_data
        
        # Add the data to the vector DB
        vector_db.add_faq_data(embedded_data)
        print(f"Added {vector_db.count()} documents to vector DB")
    else:
        print(f"Using existing vector index with {vector_db.count()} documents")


def create_out_of_domain_response() -> str:
    return """
죄송합니다. 저는 네이버 스마트스토어 FAQ 챗봇으로, 스마트스토어 관련 질문에만 답변할 수 있습니다.
스마트스토어 이용, 판매자 등록, 상품 등록, 배송, 결제, 정산 등에 관한 질문을 해주시면 도움드리겠습니다.
    """


def main():
    """엔트리 포인트"""

    parser = argparse.ArgumentParser(description="Smart Store FAQ Chatbot")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild the vector index")
    parser.add_argument("--data-path", help="Path to the FAQ data file")
    args = parser.parse_args()
    

    load_and_index_data(args.data_path, args.rebuild_index)

    print("Starting API server...")
    run_app()


if __name__ == "__main__":
    main() 