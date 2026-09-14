from datetime import datetime, timedelta, timezone

from app import models
from app.memory_service import apply_decay


def test_apply_decay_expires_old_active_episodic_memory(db_session, user):
    past = datetime.now(timezone.utc) - timedelta(days=1)
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.episodic,
        content="Old note", scope="test_scope",
        status=models.MemoryStatus.active, expires_at=past,
    )
    db_session.add(mem)
    db_session.commit()

    count = apply_decay(db_session, user.id)

    db_session.refresh(mem)
    assert count == 1
    assert mem.status == models.MemoryStatus.expired


def test_apply_decay_leaves_unexpired_memory_active(db_session, user):
    future = datetime.now(timezone.utc) + timedelta(days=10)
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.episodic,
        content="Fresh note", scope="test_scope",
        status=models.MemoryStatus.active, expires_at=future,
    )
    db_session.add(mem)
    db_session.commit()

    count = apply_decay(db_session, user.id)

    db_session.refresh(mem)
    assert count == 0
    assert mem.status == models.MemoryStatus.active


def test_apply_decay_never_touches_factual_memories(db_session, user):
    # Factual memories have no expires_at and must never be decayed, regardless
    # of age - this is the core factual/episodic behavioral distinction.
    old = datetime.now(timezone.utc) - timedelta(days=365)
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.factual,
        content="Permanent fact", scope="role:Someone",
        status=models.MemoryStatus.active, expires_at=None, created_at=old,
    )
    db_session.add(mem)
    db_session.commit()

    apply_decay(db_session, user.id)

    db_session.refresh(mem)
    assert mem.status == models.MemoryStatus.active


def test_apply_decay_ignores_already_expired_memories(db_session, user):
    past = datetime.now(timezone.utc) - timedelta(days=5)
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.episodic,
        content="Already expired", scope="test_scope",
        status=models.MemoryStatus.expired, expires_at=past,
    )
    db_session.add(mem)
    db_session.commit()

    count = apply_decay(db_session, user.id)
    assert count == 0  # already expired, shouldn't be re-counted