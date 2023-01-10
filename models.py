"""Models."""
from uuid import UUID

from pydantic import BaseModel


class Document(BaseModel):
    id: UUID
    status: str
    meta: dict


class SearchResult(Document):
    headline: str
    rank: float


class Highlight(BaseModel):
    page_number: int
    headline: str
