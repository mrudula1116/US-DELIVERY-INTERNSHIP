from datetime import datetime
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    account_id: str
    company: str
    subject: str
    body: str
    product: str
    product_area: str
    category: str
    urgency: str = Field(pattern=r"^P[1-4]$")
    plan_tier: str
    channel: str


class TicketResponse(TicketCreate):
    ticket_id: str
    status: str
    assigned_agent: str | None = None
    created_at: datetime
    updated_at: datetime
    tags: list[str] = []
    satisfaction_score: int | None = None