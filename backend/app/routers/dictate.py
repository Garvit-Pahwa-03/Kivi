from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from app.db import get_db
from app.auth import get_current_user
from app import models
from app.memory_service import ingest_dictation
from app import shortcuts as shortcuts_svc

router = APIRouter(prefix="/dictate", tags=["dictate"])


class DictateIn(BaseModel):
    text: str
    app: str = "Notes"


@router.post("")
def dictate(payload: DictateIn, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    expanded_text, applied = shortcuts_svc.expand_shortcuts(db, current_user.id, payload.text)

    record = {
        "record_id": "live-" + str(uuid.uuid4()),
        "app": payload.app,
        "raw_asr": payload.text,
        "llm_formatted": expanded_text,
        "timestamp": datetime.now(timezone.utc),
        "extra_metadata": {"shortcuts_applied": applied},
    }
    summary = ingest_dictation(db, current_user, record)
    return {
        "original_text": payload.text,
        "expanded_text": expanded_text,
        "shortcuts_applied": applied,
        "ingestion_summary": summary,
    }