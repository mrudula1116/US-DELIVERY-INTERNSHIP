from fastapi import FastAPI, HTTPException
from app.services.triage_service import triage_ticket
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Any, Dict
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.rag import AskRequest, AskResponse
from app.models.ticket import TicketCreate, TicketResponse
from app.models.account import TopUpRequest
class TriageRequest(BaseModel):
    subject: str
    body: str
    account_id: Optional[str] = None
from app.services.ticket_service import (
    create_ticket,
    list_tickets,
)

from app.services.account_service import (
    get_account,
    load_accounts,
    topup_account,
)

from app.rag.service import (
    rag_service,
    load_documents,
)
from app.rag.generator import generate_answer


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="US Delivery Internship Support Intelligence API",
    version="1.0.0",
    description=(
        "Backend service for support tickets, customer accounts, "
        "and knowledge-base question answering."
    ),
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

@app.get("/", response_class=HTMLResponse)
def home():
    index_file = BASE_DIR / "templates" / "index.html"
    return index_file.read_text(encoding="utf-8")
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "support-intelligence-api",
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    results = rag_service.search(
        question,
        top_k=3,
    )

    answer, citations = generate_answer(
        question,
        results,
    )

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
    }


@app.post("/tickets", response_model=TicketResponse)
def create_support_ticket(
    request: TicketCreate,
):

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    ticket_id = f"TKT-{int(now.timestamp())}"

    ticket = {
        **request.model_dump(),
        "ticket_id": ticket_id,
        "status": "Open",
        "assigned_agent": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "tags": [],
        "satisfaction_score": None,
    }

    created = create_ticket(ticket)

    return created


@app.get("/tickets")
def get_tickets(
    status: str | None = None,
    urgency: str | None = None,
    account_id: str | None = None,
):

    return list_tickets(
        status=status,
        urgency=urgency,
        account_id=account_id,
    )


@app.get("/accounts")
def list_customer_accounts():
    return load_accounts()


@app.get("/accounts/{account_id}/health")
def get_customer_account_health(
    account_id: str,
):

    account = get_account(account_id)

    if account is None:

        raise HTTPException(
            status_code=404,
            detail=f"Account {account_id} not found.",
        )

    return {
        **account,
        "executive_summary": (
            f"{account.get('company', 'The customer')} currently has "
            f"{account.get('open_tickets', 0)} open support tickets and "
            f"a {account.get('health_status', 'unknown')} health status."
        ),
        "open_risks": [
            {
                "risk": "Elevated support risk",
                "severity": "Medium",
                "evidence": (
                    f"{account.get('open_tickets', 0)} open ticket(s) "
                    f"and current health status of {account.get('health_status', 'unknown')}."
                ),
            }
        ],
        "talking_points": [
            "Review recent support ticket trends and escalation risk.",
            "Confirm product usage and renewal readiness.",
            "Highlight any open operational issues and next steps."
        ],
    }


@app.get("/accounts/{account_id}")
def get_customer_account(
    account_id: str,
):

    account = get_account(account_id)

    if account is None:

        raise HTTPException(
            status_code=404,
            detail=f"Account {account_id} not found.",
        )

    return account


@app.post("/accounts/{account_id}/topup")
def top_up_customer_account(
    account_id: str,
    request: TopUpRequest,
):
    if request.amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Top-up amount must be greater than zero.",
        )

    account = topup_account(
        account_id,
        request.amount,
    )

    if account is None:

        raise HTTPException(
            status_code=404,
            detail=f"Account {account_id} not found.",
        )

    return {
        "message": "Account topped up successfully.",
        "account_id": account_id,
        "amount_added": request.amount,
        "balance_usd": account["balance_usd"],
    }


@app.get("/knowledge-base")
def get_knowledge_base():

    documents = load_documents()

    return [
        {
            "title": doc.get("section"),
            "description": doc.get("content", "")[:250],
            "path": doc.get("source"),
            **doc,
        }
        for doc in documents
    ]


@app.post("/triage")
def triage_ticket_endpoint(ticket: TriageRequest):
    result = triage_ticket({
        "subject": ticket.subject,
        "body": ticket.body,
        "account_id": ticket.account_id,
    })

    return result