from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import get_current_user
from app import models
from app.orchestrator import handle_request

router = APIRouter(prefix="/hey-kivi", tags=["hey-kivi"])


class AskIn(BaseModel):
    request_text: str


@router.post("/ask")
def ask(payload: AskIn, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return handle_request(db, current_user, payload.request_text)