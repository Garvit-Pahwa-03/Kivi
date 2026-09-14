import re
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app import models


def _now():
    return datetime.now(timezone.utc)


def create_or_update_shortcut(db: Session, user_id: str, trigger_phrase: str, expansion_text: str):
    existing = db.query(models.Shortcut).filter(
        models.Shortcut.user_id == user_id,
        models.Shortcut.trigger_phrase == trigger_phrase,
    ).first()
    if existing:
        existing.expansion_text = expansion_text
        existing.active = 1
        existing.updated_at = _now()
        db.commit()
        db.refresh(existing)
        return existing

    shortcut = models.Shortcut(
        user_id=user_id, trigger_phrase=trigger_phrase, expansion_text=expansion_text,
    )
    db.add(shortcut)
    db.commit()
    db.refresh(shortcut)
    return shortcut


def list_shortcuts(db: Session, user_id: str):
    return db.query(models.Shortcut).filter(
        models.Shortcut.user_id == user_id, models.Shortcut.active == 1,
    ).order_by(models.Shortcut.updated_at.desc()).all()


def delete_shortcut(db: Session, user_id: str, shortcut_id: str) -> bool:
    shortcut = db.query(models.Shortcut).filter(
        models.Shortcut.id == shortcut_id, models.Shortcut.user_id == user_id,
    ).first()
    if not shortcut:
        return False
    shortcut.active = 0
    db.commit()
    return True


def expand_shortcuts(db: Session, user_id: str, text: str):
    """Applies every active shortcut as a case-insensitive whole-phrase substitution.
    Deterministic and order-independent by design: shortcuts are meant to be
    unambiguous phrase triggers, not overlapping fuzzy matches. Returns the
    expanded text plus a list of which shortcuts fired, for inspectability."""
    shortcuts = list_shortcuts(db, user_id)
    result = text
    applied = []
    for sc in shortcuts:
        pattern = re.compile(re.escape(sc.trigger_phrase), re.IGNORECASE)
        if pattern.search(result):
            result = pattern.sub(sc.expansion_text, result)
            applied.append({"trigger_phrase": sc.trigger_phrase, "shortcut_id": sc.id})
    return result, applied