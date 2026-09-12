from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app import models

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/memories")
def list_memories(user_name: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == user_name).first()
    if not user:
        return {"error": "user not found"}
    memories = db.query(models.Memory).filter(models.Memory.user_id == user.id).all()
    out = {"factual": [], "episodic": [], "preference": []}
    for m in memories:
        out[m.type.value].append({
            "id": m.id, "scope": m.scope, "content": m.content,
            "status": m.status.value,
            "expires_at": m.expires_at.isoformat() if m.expires_at else None,
            "created_at": m.created_at.isoformat(),
        })
    return out

@router.get("/memory-search")
def memory_search_raw(user_name: str, contains: str, db: Session = Depends(get_db)):
    """Raw substring search over ALL memory content/scope, bypassing retrieval scoring
    entirely — for diagnosing whether something was ever extracted/stored at all."""
    user = db.query(models.User).filter(models.User.name == user_name).first()
    if not user:
        return {"error": "user not found"}
    memories = db.query(models.Memory).filter(models.Memory.user_id == user.id).all()
    matches = [
        {"id": m.id, "type": m.type.value, "scope": m.scope, "content": m.content, "status": m.status.value}
        for m in memories
        if contains.lower() in m.content.lower() or contains.lower() in (m.scope or "").lower()
    ]
    return {"count": len(matches), "matches": matches}