"""FastAPI application for the Smart Store FAQ chatbot."""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import API_HOST, API_PORT
from .router import router


# Create FastAPI app
app = FastAPI(
    title="Smart Store FAQ Chatbot API",
    description="API for the Smart Store FAQ chatbot",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include router
app.include_router(router, prefix="/api")


# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Run the app
def run_app():
    """Run the FastAPI application."""
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    run_app() 