from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app import models
from app.extraction import extract_candidates

EPISODIC_DECAY_DAYS = 30


def _now():
    return datetime.now(timezone.utc)


def get_or_create_user(db: Session, name: str) -> models.User:
    user = db.query(models.User).filter(models.User.name == name).first()
    if user:
        return user
    user = models.User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def log_event(db: Session, memory_id, action, reason, detail=None):
    db.add(models.MemoryEvent(
        memory_id=memory_id, action=action, reason=reason, detail=detail or {},
    ))


def ingest_dictation(db: Session, user: models.User, record: dict, extractor_version="v1"):
    """Process one dictation record end to end: store it, extract candidates, apply
    deterministic dedup/merge/decay/conflict logic, and log every decision."""

    ts = record["timestamp"]
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)
    record = {**record, "timestamp": ts}

    existing = db.query(models.Dictation).filter(
        models.Dictation.record_id == record["record_id"]
    ).first()
    if existing:
        return {"skipped": True, "reason": "already ingested"}

    dictation = models.Dictation(
        user_id=user.id,
        record_id=record["record_id"],
        app=record["app"],
        raw_asr=record["raw_asr"],
        llm_formatted=record["llm_formatted"],
        timestamp=record["timestamp"],
        extra_metadata=record.get("extra_metadata", {}),
    )
    db.add(dictation)
    db.flush()

    candidates = extract_candidates(record["app"], str(record["timestamp"]), record["llm_formatted"])
    usage = candidates.pop("_usage", {})
    summary = {"factual": [], "episodic": [], "preference": [], "usage": usage}

    # ---- Factual: upsert by key ----
    for item in candidates["factual"]:
        key = (item.get("key") or "").strip()
        value = (item.get("value") or "").strip()
        if not key or not value:
            continue
        existing_mem = (
            db.query(models.Memory)
            .filter(
                models.Memory.user_id == user.id,
                models.Memory.type == models.MemoryType.factual,
                models.Memory.scope == key,
                models.Memory.status == models.MemoryStatus.active,
            )
            .first()
        )
        if existing_mem and existing_mem.content.strip() == value:
            db.add(models.MemoryProvenance(
                memory_id=existing_mem.id, dictation_id=dictation.id, extractor_version=extractor_version,
            ))
            log_event(db, existing_mem.id, models.EventAction.retrieved,
                      "reinforced by repeated mention", {"dictation_id": dictation.id})
            summary["factual"].append({"key": key, "action": "reinforced"})
            continue

        mem = models.Memory(
            user_id=user.id, type=models.MemoryType.factual,
            content=value, scope=key, status=models.MemoryStatus.active,
        )
        db.add(mem)
        db.flush()
        db.add(models.MemoryProvenance(
            memory_id=mem.id, dictation_id=dictation.id, extractor_version=extractor_version,
        ))
        if existing_mem:
            existing_mem.status = models.MemoryStatus.overridden
            mem.supersedes_id = existing_mem.id
            log_event(db, existing_mem.id, models.EventAction.updated,
                      f"superseded by new factual value for key={key}")
        log_event(db, mem.id, models.EventAction.created,
                  "new factual memory extracted", {"dictation_id": dictation.id})
        summary["factual"].append({"key": key, "action": "created" if not existing_mem else "updated"})

    # ---- Episodic: match by topic_key; re-reference resets decay ----
    for item in candidates["episodic"]:
        topic_key = (item.get("topic_key") or "").strip()
        text = (item.get("summary") or "").strip()
        if not topic_key or not text:
            continue
        matched = (
            db.query(models.Memory)
            .filter(
                models.Memory.user_id == user.id,
                models.Memory.type == models.MemoryType.episodic,
                models.Memory.scope == topic_key,
                models.Memory.status.in_([models.MemoryStatus.active, models.MemoryStatus.expired]),
            )
            .order_by(models.Memory.created_at.desc())
            .first()
        )
        new_expiry = record["timestamp"] + timedelta(days=EPISODIC_DECAY_DAYS)
        if matched:
            was_expired = matched.status == models.MemoryStatus.expired
            matched.status = models.MemoryStatus.active
            matched.expires_at = new_expiry
            matched.updated_at = _now()
            matched.content = text
            db.add(models.MemoryProvenance(
                memory_id=matched.id, dictation_id=dictation.id, extractor_version=extractor_version,
            ))
            log_event(db, matched.id, models.EventAction.updated,
                      "re-referenced: decay clock reset" + (" (was expired)" if was_expired else ""),
                      {"dictation_id": dictation.id, "new_expires_at": new_expiry.isoformat()})
            summary["episodic"].append({"topic_key": topic_key, "action": "decay_reset"})
        else:
            mem = models.Memory(
                user_id=user.id, type=models.MemoryType.episodic,
                content=text, scope=topic_key, status=models.MemoryStatus.active,
                expires_at=new_expiry,
            )
            db.add(mem)
            db.flush()
            db.add(models.MemoryProvenance(
                memory_id=mem.id, dictation_id=dictation.id, extractor_version=extractor_version,
            ))
            log_event(db, mem.id, models.EventAction.created,
                      "new episodic memory extracted",
                      {"dictation_id": dictation.id, "expires_at": new_expiry.isoformat()})
            summary["episodic"].append({"topic_key": topic_key, "action": "created"})

    # ---- Preference: scoped override ----
    for item in candidates["preference"]:
        scope = (item.get("scope") or "").strip()
        key = (item.get("key") or "").strip()
        value = (item.get("value") or "").strip()
        if not scope or not key or not value:
            continue
        combined_scope = f"{scope}::{key}"
        existing_mem = (
            db.query(models.Memory)
            .filter(
                models.Memory.user_id == user.id,
                models.Memory.type == models.MemoryType.preference,
                models.Memory.scope == combined_scope,
                models.Memory.status == models.MemoryStatus.active,
            )
            .first()
        )
        if existing_mem and existing_mem.content.strip() == value:
            db.add(models.MemoryProvenance(
                memory_id=existing_mem.id, dictation_id=dictation.id, extractor_version=extractor_version,
            ))
            log_event(db, existing_mem.id, models.EventAction.retrieved,
                      "preference reinforced (identical restatement)")
            summary["preference"].append({"scope": combined_scope, "action": "reinforced"})
            continue

        mem = models.Memory(
            user_id=user.id, type=models.MemoryType.preference,
            content=value, scope=combined_scope, status=models.MemoryStatus.active,
        )
        db.add(mem)
        db.flush()
        db.add(models.MemoryProvenance(
            memory_id=mem.id, dictation_id=dictation.id, extractor_version=extractor_version,
        ))
        if existing_mem:
            existing_mem.status = models.MemoryStatus.overridden
            mem.supersedes_id = existing_mem.id
            log_event(db, existing_mem.id, models.EventAction.updated,
                      f"overridden by new preference for scope={combined_scope}")
            log_event(db, mem.id, models.EventAction.created,
                      "preference override applied", {"dictation_id": dictation.id})
            summary["preference"].append({"scope": combined_scope, "action": "overridden"})
        else:
            log_event(db, mem.id, models.EventAction.created,
                      "new preference memory extracted", {"dictation_id": dictation.id})
            summary["preference"].append({"scope": combined_scope, "action": "created"})

    db.commit()
    return summary


def apply_decay(db: Session, user_id: str) -> int:
    now = _now()
    expired = (
        db.query(models.Memory)
        .filter(
            models.Memory.user_id == user_id,
            models.Memory.type == models.MemoryType.episodic,
            models.Memory.status == models.MemoryStatus.active,
            models.Memory.expires_at.isnot(None),
            models.Memory.expires_at < now,
        )
        .all()
    )
    for mem in expired:
        mem.status = models.MemoryStatus.expired
        log_event(db, mem.id, models.EventAction.decayed,
                  f"episodic memory passed 30-day expiry ({mem.expires_at.isoformat()})")
    db.commit()
    return len(expired)