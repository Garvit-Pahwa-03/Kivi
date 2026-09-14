from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DictationIn(BaseModel):
    record_id: str
    app: str
    raw_asr: str
    llm_formatted: str
    timestamp: datetime
    extra_metadata: Dict[str, Any] = {}


class CorpusIn(BaseModel):
    user_name: str
    company: Optional[str] = None
    records: List[DictationIn]
    
class ShortcutIn(BaseModel):
    user_name: str
    trigger_phrase: str
    expansion_text: str


class DictateIn(BaseModel):
    user_name: str
    text: str
    app: str = "Notes"
    
class SignupIn(BaseModel):
    name: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str