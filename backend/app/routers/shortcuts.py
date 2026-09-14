from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import get_current_user
from app import models
from app import shortcuts as shortcuts_svc

router = APIRouter(prefix="/shortcuts", tags=["shortcuts"])


class ShortcutTeach(BaseModel):
    trigger_phrase: str
    expansion_text: str


@router.post("")
def teach_shortcut(payload: ShortcutTeach, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    sc = shortcuts_svc.create_or_update_shortcut(db, current_user.id, payload.trigger_phrase, payload.expansion_text)
    return {"id": sc.id, "trigger_phrase": sc.trigger_phrase, "expansion_text": sc.expansion_text}


@router.get("")
def get_shortcuts(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = shortcuts_svc.list_shortcuts(db, current_user.id)
    return {"count": len(items), "shortcuts": [
        {"id": s.id, "trigger_phrase": s.trigger_phrase, "expansion_text": s.expansion_text,
         "updated_at": s.updated_at.isoformat()}
        for s in items
    ]}


@router.delete("/{shortcut_id}")
def remove_shortcut(shortcut_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = shortcuts_svc.delete_shortcut(db, current_user.id, shortcut_id)
    return {"deleted": ok}