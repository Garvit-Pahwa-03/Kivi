from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import get_current_user
from app import models
from app.schemas import CorpusIn
from app.memory_service import ingest_dictation, apply_decay

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/corpus")
def ingest_corpus(corpus: CorpusIn, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = []
    for record in corpus.records:
        summary = ingest_dictation(db, current_user, record.model_dump())
        results.append({"record_id": record.record_id, "summary": summary})
    decayed_count = apply_decay(db, current_user.id)
    return {
        "user_id": current_user.id,
        "ingested": len(results),
        "decayed_on_ingest": decayed_count,
        "results": results,
    }