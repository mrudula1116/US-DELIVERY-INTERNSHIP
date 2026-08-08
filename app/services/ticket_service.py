import json
from pathlib import Path
from typing import List, Dict, Any, Optional


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
TICKETS_FILE = BASE_DIR / "Data" / "tickets.json"


# ---------------------------------------------------------
# Ticket Loading
# ---------------------------------------------------------

def load_tickets() -> List[Dict[str, Any]]:
    """
    Load support tickets from Data/tickets.json.

    Handles both:
    - a JSON list
    - a JSON object containing a ticket list
    """

    if not TICKETS_FILE.exists():
        raise FileNotFoundError(
            f"Tickets file not found: {TICKETS_FILE}"
        )

    with TICKETS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    # Normal format: list of tickets
    if isinstance(data, list):
        return data

    # Handle common wrapped formats
    if isinstance(data, dict):

        for key in (
            "tickets",
            "data",
            "items"
        ):
            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError(
        "Unexpected tickets.json format. "
        "Expected a list of tickets."
    )


# ---------------------------------------------------------
# Ticket Lookup
# ---------------------------------------------------------

def get_ticket_by_id(
    ticket_id: str
) -> Optional[Dict[str, Any]]:
    """
    Return a ticket by ticket_id.
    """

    tickets = load_tickets()

    for ticket in tickets:

        if ticket.get("ticket_id") == ticket_id:
            return ticket

    return None


# ---------------------------------------------------------
# Ticket Text
# ---------------------------------------------------------

def ticket_to_text(
    ticket: Dict[str, Any]
) -> str:
    """
    Convert a structured ticket into text suitable
    for triage and RAG retrieval.
    """

    subject = ticket.get("subject", "")
    body = ticket.get("body", "")

    return f"{subject}\n\n{body}".strip()


def create_ticket(ticket: dict) -> dict:
    """
    Create a new support ticket.

    The function:
    1. Loads existing tickets
    2. Generates the next ticket ID
    3. Adds the new ticket
    4. Saves the updated ticket list
    5. Returns the created ticket
    """

    tickets = load_tickets()

    # Generate next ticket ID
    if tickets:
        numeric_ids = []

        for existing_ticket in tickets:
            ticket_id = str(existing_ticket.get("ticket_id", ""))

            if ticket_id.startswith("TKT-"):
                try:
                    numeric_ids.append(
                        int(ticket_id.replace("TKT-", ""))
                    )
                except ValueError:
                    pass

        next_number = max(numeric_ids, default=0) + 1

    else:
        next_number = 1

    new_ticket = ticket.copy()

    new_ticket["ticket_id"] = f"TKT-{next_number:04d}"

    tickets.append(new_ticket)

    save_tickets(tickets)

    return new_ticket
def list_tickets(
    status: str | None = None,
    urgency: str | None = None,
    account_id: str | None = None,
):
    """Return support tickets optionally filtered by status, urgency, or query."""

    tickets = load_tickets()

    if status is None and urgency is None and account_id is None:
        return tickets

    status = status.lower().strip() if status else None
    urgency = urgency.lower().strip() if urgency else None
    query = account_id.lower().strip() if account_id else None

    filtered = []

    for ticket in tickets:

        if status:
            if str(ticket.get("status", "")).lower() != status:
                continue

        if urgency:
            urgency_value = str(
                ticket.get("urgency", "") or ticket.get("priority", "")
            ).lower()

            if urgency_value != urgency:
                continue

        if query:
            searchable = " ".join([
                str(ticket.get("ticket_id", "")),
                str(ticket.get("account_id", "")),
                str(ticket.get("subject", "")),
                str(ticket.get("body", "")),
            ]).lower()

            if query not in searchable:
                continue

        filtered.append(ticket)

    return filtered


def get_ticket(ticket_id: str):
    """Return a ticket by ID, or None if not found."""
    tickets = load_tickets()

    for ticket in tickets:
        if str(ticket.get("ticket_id")) == str(ticket_id):
            return ticket

    return None


def create_ticket(ticket: dict) -> dict:
    """Create and persist a new support ticket."""

    tickets = load_tickets()

    numeric_ids = []

    for existing_ticket in tickets:
        ticket_id = str(existing_ticket.get("ticket_id", ""))

        if ticket_id.startswith("TKT-"):
            try:
                numeric_ids.append(
                    int(ticket_id.replace("TKT-", ""))
                )
            except ValueError:
                pass

    next_number = max(numeric_ids, default=0) + 1

    new_ticket = ticket.copy()
    new_ticket["ticket_id"] = f"TKT-{next_number:04d}"

    tickets.append(new_ticket)
    save_tickets(tickets)

    return new_ticket