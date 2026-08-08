from pydantic import BaseModel


class TopUpRequest(BaseModel):
    amount: float


class AccountResponse(BaseModel):
    account_id: str
    company: str
    tam: str
    plan_tier: str
    arr_usd: int
    seats_licensed: int
    seats_active: int
    products: list[str]
    health_status: str
    usage_trend: str
    open_tickets: int
    p1_tickets_last_30d: int
    renewal_date: str
    last_qbr_date: str
    escalation_notes: list[str]
    nps_score: int | None = None
    primary_contact: dict
    integrations_active: list[str]
    region: str
    industry: str
    balance_usd: float | None = None