import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Enum as SAEnum, Integer, Float, JSON
)
from sqlalchemy.orm import relationship

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryType(str, enum.Enum):
    factual = "factual"
    episodic = "episodic"
    preference = "preference"


class MemoryStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    deleted = "deleted"
    overridden = "overridden"


class EventAction(str, enum.Enum):
    created = "created"
    retrieved = "retrieved"
    updated = "updated"
    rejected = "rejected"
    decayed = "decayed"
    deleted = "deleted"


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=_now)

    dictations = relationship("Dictation", back_populates="user")
    memories = relationship("Memory", back_populates="user")


class Dictation(Base):
    """A single transcript-like record: raw ASR + LLM-formatted text + app/time metadata."""
    __tablename__ = "dictations"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    record_id = Column(String, unique=True, nullable=False)  # external/corpus id
    app = Column(String, nullable=False)          # e.g. Slack, Docs, Outlook, Notes
    raw_asr = Column(Text, nullable=False)
    llm_formatted = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)  # when the dictation happened
    extra_metadata = Column(JSON, default=dict)
    ingested_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="dictations")
    provenance_links = relationship("MemoryProvenance", back_populates="dictation")


class Memory(Base):
    """Unified store for factual / episodic / preference memory."""
    __tablename__ = "memories"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(SAEnum(MemoryType), nullable=False)
    content = Column(Text, nullable=False)          # human-readable memory statement
    scope = Column(String, nullable=True)            # e.g. app name, for preference memory
    status = Column(SAEnum(MemoryStatus), default=MemoryStatus.active)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now)
    expires_at = Column(DateTime, nullable=True)      # episodic decay deadline
    supersedes_id = Column(String, ForeignKey("memories.id"), nullable=True)

    user = relationship("User", back_populates="memories")
    provenance_links = relationship("MemoryProvenance", back_populates="memory")


class MemoryProvenance(Base):
    """Links a memory back to the exact dictation(s) it was extracted from."""
    __tablename__ = "memory_provenance"
    id = Column(String, primary_key=True, default=_uuid)
    memory_id = Column(String, ForeignKey("memories.id"), nullable=False)
    dictation_id = Column(String, ForeignKey("dictations.id"), nullable=False)
    extractor_version = Column(String, default="v1")
    extraction_confidence = Column(Float, default=1.0)

    memory = relationship("Memory", back_populates="provenance_links")
    dictation = relationship("Dictation", back_populates="provenance_links")


class MemoryEvent(Base):
    """Append-only audit log: every create/retrieve/update/reject/decay/delete, with a reason."""
    __tablename__ = "memory_events"
    id = Column(String, primary_key=True, default=_uuid)
    memory_id = Column(String, ForeignKey("memories.id"), nullable=True)
    action = Column(SAEnum(EventAction), nullable=False)
    reason = Column(Text, nullable=True)
    detail = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_now)


class HeyKiviTurn(Base):
    """One Hey Kivi request/response, with tools used and cost/latency for eval."""
    __tablename__ = "hey_kivi_turns"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    request_text = Column(Text, nullable=False)
    tools_called = Column(JSON, default=list)
    memories_used = Column(JSON, default=list)   # list of memory ids
    response_text = Column(Text, nullable=True)
    abstained = Column(Integer, default=0)        # 0/1
    latency_ms = Column(Integer, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_now)