import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_DIMENSION = 384  # 텍스트 임베딩 dim

COLLECTION_NAME = "faq_collection"
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")

FAQ_DATA_PATH = os.getenv("FAQ_DATA_PATH", "faq_embeddings_with_vectors_overlapped.pkl")

MAX_TOKENS_PER_CHUNK = 6000
OVERLAP_RATIO = 0.2

MAX_CONVERSATION_HISTORY = 5 

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

DOMAIN_KEYWORDS = [
    "스마트스토어", "판매", "상품", "등록", "배송", "결제", "정산", "환불", 
    "취소", "반품", "교환", "네이버", "쇼핑", "가입", "계정", "판매자", 
    "구매자", "고객", "주문", "정책", "수수료", "정보", "인증", "심사"
] 


