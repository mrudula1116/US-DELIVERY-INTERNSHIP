import json

from app.services.ticket_service import load_tickets
from app.services.triage_service import triage_ticket


def main():

    tickets = load_tickets()

    if not tickets:
        raise RuntimeError(
            "No tickets found."
        )

    ticket = tickets[0]

    result = triage_ticket(ticket)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()