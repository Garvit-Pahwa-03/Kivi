from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import CorpusIn
from app.memory_service import get_or_create_user, ingest_dictation, apply_decay

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/corpus")
def ingest_corpus(corpus: CorpusIn, db: Session = Depends(get_db)):
    user = get_or_create_user(db, corpus.user_name)
    results = []
    for record in corpus.records:
        summary = ingest_dictation(db, user, record.model_dump())
        results.append({"record_id": record.record_id, "summary": summary})
    decayed_count = apply_decay(db, user.id)
    return {
        "user_id": user.id,
        "ingested": len(results),
        "decayed_on_ingest": decayed_count,
        "results": results,
    }