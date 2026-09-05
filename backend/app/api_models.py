from typing import Optional

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    conversation_context: Optional[str] = None


class Source(BaseModel):
    document_id: str
    trial_id: Optional[str] = None
    source_type: str
    section: Optional[str] = None
    content: Optional[str] = None
    relevance_score: Optional[float] = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]