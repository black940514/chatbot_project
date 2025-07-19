# 네이버 스마트스토어 FAQ 챗봇

스마트스토어 FAQ 데이터를 기반으로 한 RAG(Retrieval-Augmented Generation) 챗봇 API입니다.

## 기능

- 스마트스토어 FAQ 데이터 기반 질의응답
- 대화 컨텍스트 관리 (세션별 대화 기록 유지)
- 스트리밍 응답 지원
- 도메인 외 질문 필터링
- 후속 질문 추천

## 기술 스택

- **언어**: Python 3.12
- **프레임워크**: FastAPI
- **임베딩 모델**: OpenAI text-embedding-3-small
- **LLM**: OpenAI gpt-4o-mini
- **벡터 DB**: ChromaDB
- **기타 라이브러리**: tiktoken, numpy, tqdm 등

## 프로젝트 구조

```
src/
  ├── cox/
  │   ├── __init__.py
  │   ├── config.py           # 환경 설정 관리
  │   ├── data/
  │   │   ├── __init__.py
  │   │   ├── loader.py       # 데이터 로드 모듈
  │   │   └── preprocessor.py # 데이터 전처리 모듈
  │   ├── embedding/
  │   │   ├── __init__.py
  │   │   ├── chunker.py      # 오버랩 청킹 모듈
  │   │   └── vectorizer.py   # 임베딩 생성 모듈
  │   ├── retrieval/
  │   │   ├── __init__.py
  │   │   ├── vector_db.py    # 벡터 DB 관리 모듈
  │   │   └── retriever.py    # 유사 문서 검색 모듈
  │   ├── memory/
  │   │   ├── __init__.py
  │   │   └── conversation.py # 대화 컨텍스트 관리 모듈
  │   ├── generation/
  │   │   ├── __init__.py
  │   │   ├── llm.py          # LLM 호출 모듈
  │   │   └── prompt.py       # 프롬프트 템플릿 모듈
  │   └── api/
  │       ├── __init__.py
  │       ├── app.py          # FastAPI 앱 정의
  │       └── router.py       # API 엔드포인트 정의
  └── main.py                 # 애플리케이션 진입점
```

## 설치 및 실행

### 1. 환경 설정

먼저 프로젝트를 클론하고 필요한 패키지를 설치합니다.

```bash
# 저장소 클론
git clone https://github.com/your-username/smart-store-faq-chatbot.git
cd smart-store-faq-chatbot

# 가상환경 생성 및 활성화 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -e .
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가합니다.

```
OPENAI_API_KEY=your-openai-api-key
VECTOR_DB_PATH=./chroma_db
FAQ_DATA_PATH=./faq_embeddings_with_vectors_overlapped.pkl
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. 데이터 준비

FAQ 데이터를 준비하고 임베딩합니다.

```bash
# 이미 임베딩된 데이터가 있는 경우
python -m src.main --data-path=path/to/your/data.pkl

# 인덱스를 재구축해야 하는 경우
python -m src.main --data-path=path/to/your/data.pkl --rebuild-index
```

### 4. API 서버 실행

```bash
python -m src.main
```

서버가 실행되면 `http://localhost:8000`에서 API를 사용할 수 있습니다.

## API 엔드포인트

### 채팅 API

#### POST /api/chat

일반 채팅 API 엔드포인트입니다.

**요청**:
```json
{
  "session_id": "optional-session-id",
  "question": "미성년자도 판매 회원 등록이 가능한가요?"
}
```

**응답**:
```json
{
  "session_id": "session-id",
  "answer": "네이버 스마트스토어는 만 14세 미만의 개인(개인 사업자 포함) 또는 법인사업자는 입점이 불가함을 양해 부탁 드립니다...",
  "follow_up_questions": [
    "등록에 필요한 서류 안내해드릴까요?",
    "등록 절차는 얼마나 오래 걸리는지 안내가 필요하신가요?"
  ]
}
```

#### POST /api/chat/stream

스트리밍 채팅 API 엔드포인트입니다.

**요청**:
```json
{
  "session_id": "optional-session-id",
  "question": "미성년자도 판매 회원 등록이 가능한가요?"
}
```

**응답**: Server-Sent Events (SSE) 형식으로 응답이 스트리밍됩니다.

#### GET /api/chat/history/{session_id}

대화 기록을 조회합니다.

#### DELETE /api/chat/history/{session_id}

대화 기록을 삭제합니다.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.