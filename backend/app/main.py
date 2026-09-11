from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.llm_client import chat
from app.routers import ingest, debug

app = FastAPI(title="Kivi Semantic Memory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(debug.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug/llm-ping")
def llm_ping():
    try:
        result = chat([{"role": "user", "content": "Reply with exactly: pong"}])
        return result
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}