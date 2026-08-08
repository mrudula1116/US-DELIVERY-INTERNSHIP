from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class Citation(BaseModel):
    source: str
    section: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]