from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.llm_client import chat
from app.routers import ingest, debug, hey_kivi
from app.routers import ingest, debug, hey_kivi, shortcuts, dictate
from app.routers import ingest, debug, hey_kivi, shortcuts, dictate, auth as auth_router


app = FastAPI(title="Kivi Semantic Memory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(debug.router)
app.include_router(hey_kivi.router)
app.include_router(shortcuts.router)
app.include_router(dictate.router)
app.include_router(auth_router.router)


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