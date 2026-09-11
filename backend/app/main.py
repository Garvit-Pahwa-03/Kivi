from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.llm_client import chat

app = FastAPI(title="Kivi Semantic Memory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug/llm-ping")
def llm_ping():
    """Sanity check that the Sarvam API key + model work end to end."""
    result = chat([{"role": "user", "content": "Reply with exactly: pong"}])
    return result