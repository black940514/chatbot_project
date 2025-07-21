import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import API_HOST, API_PORT
from .router import router


app = FastAPI(
    title="Cox Smart Store FAQ Chatbot API",
    version="0.1.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    """
    상태 확인 엔드포인트
    """
    return {"status": "ok"}

def run_app():
    """
    FastAPI 애플리케이션 실행
    """
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    run_app() 