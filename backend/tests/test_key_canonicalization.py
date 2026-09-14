from app import models
from app.memory_service import _find_existing_by_normalized_key


def test_find_existing_matches_exact_key(db_session, user):
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.factual,
        content="Project Comet is the billing system migration.",
        scope="PRJ-CMT", status=models.MemoryStatus.active,
    )
    db_session.add(mem)
    db_session.commit()

    found = _find_existing_by_normalized_key(db_session, user.id, models.MemoryType.factual, "PRJ-CMT")
    assert found is not None
    assert found.id == mem.id


def test_find_existing_matches_suffixed_variant_key(db_session, user):
    # Regression test for the real PRJ-CMT / PRJ-CMT_project_comet key-fork bug.
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.factual,
        content="Project Comet is the billing system migration.",
        scope="PRJ-CMT", status=models.MemoryStatus.active,
    )
    db_session.add(mem)
    db_session.commit()

    found = _find_existing_by_normalized_key(
        db_session, user.id, models.MemoryType.factual, "PRJ-CMT_project_comet",
    )
    assert found is not None
    assert found.id == mem.id


def test_find_existing_returns_none_for_genuinely_different_key(db_session, user):
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.factual,
        content="Project Falcon is the onboarding redesign.",
        scope="PRJ-FLC", status=models.MemoryStatus.active,
    )
    db_session.add(mem)
    db_session.commit()

    found = _find_existing_by_normalized_key(db_session, user.id, models.MemoryType.factual, "PRJ-CMT")
    assert found is None


def test_find_existing_ignores_non_active_memories(db_session, user):
    mem = models.Memory(
        user_id=user.id, type=models.MemoryType.factual,
        content="Old value", scope="PRJ-CMT", status=models.MemoryStatus.overridden,
    )
    db_session.add(mem)
    db_session.commit()

    found = _find_existing_by_normalized_key(db_session, user.id, models.MemoryType.factual, "PRJ-CMT")
    assert found is None