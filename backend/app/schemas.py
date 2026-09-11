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