# 네이버 스마트스토어 FAQ 챗봇
스마트스토어 FAQ 데이터를 기반으로 한 RAG(Retrieval-Augmented Generation) 챗봇 API입니다.

## 기능

- 스마트스토어 FAQ 데이터 기반 질의응답
- 대화 컨텍스트 관리 (세션별 대화 기록 유지)
- 스트리밍 응답 지원
- 도메인 외 질문 필터링
- 후속 질문 추천

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