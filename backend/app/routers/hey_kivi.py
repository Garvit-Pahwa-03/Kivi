from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.memory_service import get_or_create_user
from app.orchestrator import handle_request

router = APIRouter(prefix="/hey-kivi", tags=["hey-kivi"])


class AskIn(BaseModel):
    user_name: str
    request_text: str


@router.post("/ask")
def ask(payload: AskIn, db: Session = Depends(get_db)):
    user = get_or_create_user(db, payload.user_name)
    return handle_request(db, user, payload.request_text)