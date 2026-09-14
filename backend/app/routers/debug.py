from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import get_current_user
from app import models

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/memories")
def list_memories(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    memories = db.query(models.Memory).filter(models.Memory.user_id == current_user.id).all()
    out = {"factual": [], "episodic": [], "preference": []}
    for m in memories:
        out[m.type.value].append({
            "id": m.id, "scope": m.scope, "content": m.content,
            "status": m.status.value,
            "expires_at": m.expires_at.isoformat() if m.expires_at else None,
            "created_at": m.created_at.isoformat(),
        })
    return out


@router.get("/dictations")
def list_dictations(app: str = None, limit: int = 50, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(models.Dictation).filter(models.Dictation.user_id == current_user.id)
    if app:
        q = q.filter(models.Dictation.app == app)
    records = q.order_by(models.Dictation.timestamp.desc()).limit(limit).all()
    return {
        "count": len(records),
        "dictations": [{
            "id": d.id, "record_id": d.record_id, "app": d.app,
            "raw_asr": d.raw_asr, "llm_formatted": d.llm_formatted,
            "timestamp": d.timestamp.isoformat(),
        } for d in records],
    }


@router.get("/memory-search")
def memory_search_raw(contains: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    memories = db.query(models.Memory).filter(models.Memory.user_id == current_user.id).all()
    matches = [
        {"id": m.id, "type": m.type.value, "scope": m.scope, "content": m.content, "status": m.status.value}
        for m in memories
        if contains.lower() in m.content.lower() or contains.lower() in (m.scope or "").lower()
    ]
    return {"count": len(matches), "matches": matches}