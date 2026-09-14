from app import models, retrieval
from app.llm_client import chat
from app.memory_service import log_event


def tool_search_episodic(db, user_id, keywords=None, app=None, start=None, end=None, top_k=3):
    results = retrieval.search_dictations(db, user_id, keywords=keywords, app=app, start=start, end=end, top_k=top_k)
    return {"found": len(results) > 0, "results": results}


def tool_recall_fact(db, user_id, query, top_k=3):
    from app import shortcuts as shortcuts_svc
    from app.retrieval import _rank_by_overlap

    factual = retrieval.search_memories(db, user_id, query, mem_type=models.MemoryType.factual, top_k=top_k)
    episodic = retrieval.search_memories(db, user_id, query, mem_type=models.MemoryType.episodic, top_k=top_k)

    shortcut_results = []
    all_shortcuts = shortcuts_svc.list_shortcuts(db, user_id)
    if all_shortcuts:
        ranked = _rank_by_overlap(
            query, all_shortcuts, lambda s: s.trigger_phrase + " " + s.expansion_text,
            lambda s: s.updated_at, top_k,
        )
        shortcut_results = [{
            "memory_id": s.id, "type": "shortcut", "scope": s.trigger_phrase,
            "content": "\"" + s.trigger_phrase + "\" expands to: " + s.expansion_text,
            "score": round(score, 2), "reason": "matched terms " + str(sorted(overlap)),
        } for s, overlap, score, _ in ranked]

    combined = sorted(factual + episodic + shortcut_results, key=lambda r: -(r["score"] or 0))[:top_k]
    for r in combined:
        if r["type"] != "shortcut":
            log_event(db, r["memory_id"], models.EventAction.retrieved, "retrieved for Hey Kivi query: " + query)
    db.commit()
    return {"found": len(combined) > 0, "results": combined}

def tool_recall_preference(db, user_id, app_scope, key_hint="formatting_style", top_k=3):
    results = retrieval.latest_active_by_scope_prefix(
        db, user_id, models.MemoryType.preference, scope_prefix=f"{app_scope}::", top_k=top_k,
    )
    for r in results:
        log_event(db, r["memory_id"], models.EventAction.retrieved, "retrieved for Hey Kivi preference query")
    db.commit()
    return {"found": len(results) > 0, "results": results}

def tool_upsert_preference(db, user_id, app_scope, key, value):
    combined_scope = f"{app_scope}::{key}"
    existing = db.query(models.Memory).filter(
        models.Memory.user_id == user_id,
        models.Memory.type == models.MemoryType.preference,
        models.Memory.scope == combined_scope,
        models.Memory.status == models.MemoryStatus.active,
    ).first()

    mem = models.Memory(
        user_id=user_id, type=models.MemoryType.preference,
        content=value, scope=combined_scope, status=models.MemoryStatus.active,
    )
    db.add(mem)
    db.flush()
    if existing:
        existing.status = models.MemoryStatus.overridden
        mem.supersedes_id = existing.id
        log_event(db, existing.id, models.EventAction.updated, "overridden via Hey Kivi explicit instruction")
    log_event(db, mem.id, models.EventAction.created, "created via Hey Kivi explicit instruction")
    db.commit()
    return {"memory_id": mem.id, "scope": combined_scope, "content": value, "overrode_previous": existing is not None}


def tool_summarize_period(db, user_id, start, end, keywords=None, app=None):
    from datetime import datetime, timedelta, timezone
    if start is None:
        start = datetime.now(timezone.utc) - timedelta(days=30)
    if end is None:
        end = datetime.now(timezone.utc)

    dictations = retrieval.search_dictations(db, user_id, keywords=keywords, app=app, start=start, end=end, top_k=15)
    episodic = db.query(models.Memory).filter(
        models.Memory.user_id == user_id, models.Memory.type == models.MemoryType.episodic,
        models.Memory.status == models.MemoryStatus.active,
        models.Memory.updated_at >= start, models.Memory.updated_at <= end,
    ).all()
    return {
        "found": len(dictations) > 0 or len(episodic) > 0,
        "dictations": dictations,
        "episodic_memories": [{"memory_id": m.id, "scope": m.scope, "content": m.content} for m in episodic],
    }


def tool_polish_text(db, user_id, raw_text, target_app):
    pref_result = tool_recall_preference(db, user_id, target_app)
    preferences = [r["content"] for r in pref_result["results"]]
    pref_text = "\n".join(f"- {p}" for p in preferences) if preferences else \
        "(no stored preferences for this app — use clear, professional formatting by default)"

    prompt = f"""Rewrite the following raw dictation into polished, well-formatted text suitable for {target_app}.
Apply these known formatting preferences for {target_app}:
{pref_text}

Raw text:
{raw_text}

Return ONLY the polished text, nothing else."""
    result = chat([{"role": "user", "content": prompt}], temperature=0.3)
    return {
        "polished_text": (result["content"] or "").strip(),
        "preferences_applied": pref_result["results"],
        "usage": {"prompt_tokens": result["prompt_tokens"], "completion_tokens": result["completion_tokens"]},
    }
    
def tool_recall_shortcut(db, user_id, query, top_k=3):
    from app import shortcuts as shortcuts_svc
    from app.retrieval import _rank_by_overlap

    all_shortcuts = shortcuts_svc.list_shortcuts(db, user_id)
    if not all_shortcuts:
        return {"found": False, "results": []}

    ranked = _rank_by_overlap(
        query, all_shortcuts,
        lambda s: s.trigger_phrase + " " + s.expansion_text,
        lambda s: s.updated_at,
        top_k,
    )
    results = [{
        "shortcut_id": s.id, "trigger_phrase": s.trigger_phrase, "expansion_text": s.expansion_text,
        "score": round(score, 2), "reason": "matched terms " + str(sorted(overlap)),
    } for s, overlap, score, _ in ranked]
    return {"found": len(results) > 0, "results": results}