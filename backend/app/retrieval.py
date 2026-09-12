import math
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app import models

STATIC_STOPWORDS = {
    "a", "an", "the", "of", "on", "in", "to", "for", "with", "and", "or", "is", "are",
    "was", "were", "be", "been", "being", "that", "this", "these", "those", "i", "you",
    "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their",
    "what", "who", "whom", "which", "right", "now", "does", "do", "did", "stand", "status", "about",
}
MIN_SCORE = 0.3  # filters out matches supported only by near-universal terms


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if len(t) > 1]  # drop single-character fragments (possessive 's', stray initials)


def _idf_weights(query_tokens: List[str], doc_token_sets: List[set]) -> Dict[str, float]:
    n = len(doc_token_sets) or 1
    weights = {}
    for t in set(query_tokens):
        if t in STATIC_STOPWORDS:
            continue
        df = sum(1 for s in doc_token_sets if t in s)
        weights[t] = math.log((n + 1) / (df + 1)) + 0.1  # small floor avoids hard zero-outs
    return weights


DISTINCTIVE_RATIO = 0.55
MIN_COVERAGE = 0.5  # at least half the query's significant terms must be present


def _rank_by_overlap(query: str, items, text_fn, ts_fn, top_k=5):
    q_tokens = _tokenize(query)
    doc_token_sets = [set(_tokenize(text_fn(i))) for i in items]
    weights = _idf_weights(q_tokens, doc_token_sets)
    if not weights:
        return []

    global_max_weight = max(weights.values())
    required_weight = global_max_weight * DISTINCTIVE_RATIO
    total_sig_terms = len(weights)

    scored = []
    for item, doc_tokens in zip(items, doc_token_sets):
        overlap = {t for t in weights if t in doc_tokens}
        if not overlap:
            continue
        best_term_weight = max(weights[t] for t in overlap)
        coverage = len(overlap) / total_sig_terms
        # A match must EITHER contain a highly distinctive term (catches short, precise
        # queries like an acronym) OR cover a solid fraction of the query's terms (catches
        # queries with several moderately-common words and no single rare anchor). Requiring
        # only one of these, not both unconditionally, is what makes both q3-style
        # (single rare token) and q8-style (many common tokens) queries work without a
        # separate special case for either.
        if best_term_weight < required_weight and coverage < MIN_COVERAGE:
            continue
        raw_score = sum(weights[t] for t in overlap)
        length_penalty = math.sqrt(len(doc_tokens)) if doc_tokens else 1.0
        score = raw_score / length_penalty
        scored.append((item, overlap, score, ts_fn(item).timestamp()))

    scored.sort(key=lambda x: (-x[2], -x[3]))
    return scored[:top_k]

def search_dictations(
    db: Session, user_id: str,
    keywords: Optional[str] = None, app: Optional[str] = None,
    start: Optional[datetime] = None, end: Optional[datetime] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    q = db.query(models.Dictation).filter(models.Dictation.user_id == user_id)
    if app:
        q = q.filter(models.Dictation.app == app)
    if start:
        q = q.filter(models.Dictation.timestamp >= start)
    if end:
        q = q.filter(models.Dictation.timestamp <= end)
    candidates = q.order_by(models.Dictation.timestamp.desc()).all()
    if not candidates:
        return []

    if not keywords or not keywords.strip():
        return [{
            "dictation_id": d.id, "record_id": d.record_id, "app": d.app,
            "timestamp": d.timestamp.isoformat(), "text": d.llm_formatted,
            "score": None, "reason": "matched by time/app filter only, no keyword query",
        } for d in candidates[:top_k]]

    ranked = _rank_by_overlap(keywords, candidates, lambda d: d.llm_formatted, lambda d: d.timestamp, top_k)
    return [{
        "dictation_id": d.id, "record_id": d.record_id, "app": d.app,
        "timestamp": d.timestamp.isoformat(), "text": d.llm_formatted,
        "score": round(score, 2),
        "reason": f"IDF-weighted match on terms {sorted(overlap)} (score={round(score,2)})",
    } for d, overlap, score, _ in ranked]


def search_memories(
    db: Session, user_id: str, query: str,
    mem_type: Optional[models.MemoryType] = None,
    scope_prefix: Optional[str] = None, top_k: int = 3,
) -> List[Dict[str, Any]]:
    q = db.query(models.Memory).filter(
        models.Memory.user_id == user_id, models.Memory.status == models.MemoryStatus.active,
    )
    if mem_type:
        q = q.filter(models.Memory.type == mem_type)
    if scope_prefix:
        q = q.filter(models.Memory.scope.like(f"{scope_prefix}%"))
    candidates = q.order_by(models.Memory.updated_at.desc()).all()
    if not candidates:
        return []

    ranked = _rank_by_overlap(
        query, candidates, lambda m: m.content + " " + (m.scope or ""), lambda m: m.updated_at, top_k,
    )
    return [{
        "memory_id": m.id, "type": m.type.value, "scope": m.scope, "content": m.content,
        "score": round(score, 2),
        "reason": f"IDF-weighted match on terms {sorted(overlap)} (score={round(score,2)})",
    } for m, overlap, score, _ in ranked]


def latest_active_by_scope_prefix(
    db: Session, user_id: str, mem_type: models.MemoryType, scope_prefix: str, top_k: int = 3,
) -> List[Dict[str, Any]]:
    candidates = (
        db.query(models.Memory)
        .filter(
            models.Memory.user_id == user_id, models.Memory.type == mem_type,
            models.Memory.status == models.MemoryStatus.active,
            models.Memory.scope.like(f"{scope_prefix}%"),
        )
        .order_by(models.Memory.updated_at.desc())
        .limit(top_k)
        .all()
    )
    return [{
        "memory_id": m.id, "type": m.type.value, "scope": m.scope, "content": m.content,
        "score": None, "reason": f"scope-matched (prefix '{scope_prefix}'), no keyword ranking needed",
    } for m in candidates]