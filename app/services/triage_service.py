from typing import Dict, Any

from app.rag.service import rag_service


# =========================================================
# Product detection
# =========================================================

PRODUCTS = [
    "DataBridge Pro",
    "CloudSync",
    "AnalyticsHub",
    "SecureVault",
    "WorkflowEngine",
]


def detect_product(text: str) -> str:
    text_lower = text.lower()

    for product in PRODUCTS:
        if product.lower() in text_lower:
            return product

    return "Unknown"


# =========================================================
# Category detection
# =========================================================

def detect_category(text: str) -> str:
    text_lower = text.lower()

    rules = {
        "Billing": [
            "billing",
            "invoice",
            "payment",
            "charge",
            "seat",
            "plan",
            "upgrade",
            "downgrade",
        ],

        "Performance": [
            "slow",
            "slowness",
            "timeout",
            "timed out",
            "latency",
            "performance",
            "taking too long",
            "throughput",
            "degradation",
            "degraded",
        ],

        "Integration": [
            "integration",
            "oauth",
            "salesforce",
            "snowflake",
            "slack",
            "webhook",
            "api",
        ],

        "Data Loss": [
            "missing data",
            "missing records",
            "lost data",
            "data loss",
            "corrupt",
            "corrupted",
            "disappeared",
        ],

        "Onboarding": [
            "new customer",
            "getting started",
            "setup",
            "onboarding",
            "configure",
            "configuration",
        ],

        "Feature Request": [
            "feature request",
            "would like",
            "request",
            "support bulk",
            "need bulk",
        ],

        "How-To": [
            "how do i",
            "how to",
            "best practice",
            "guide",
            "help me configure",
        ],

        "Bug": [
            "bug",
            "broken",
            "not working",
            "fails",
            "failure",
            "error",
        ],
    }

    for category, keywords in rules.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category

    return "Bug"


# =========================================================
# Urgency detection
# =========================================================

def detect_urgency(text: str) -> Dict[str, str]:
    text_lower = text.lower()

    # -----------------------------------------------------
    # P1 — critical impact
    # -----------------------------------------------------

    p1_keywords = [
        "business continuity",
        "business stopped",
        "production down",
        "completely down",
        "critical data",
        "critical issue",
        "all users blocked",
        "immediately",
        "urgent",
        "p1",
    ]

    for keyword in p1_keywords:
        if keyword in text_lower:
            return {
                "urgency": "P1",
                "reason": (
                    f"Critical-impact language detected: '{keyword}'. "
                    "The ticket indicates potentially severe business impact."
                ),
            }

    # -----------------------------------------------------
    # P2 — major impact
    # -----------------------------------------------------

    p2_keywords = [
        "major impact",
        "significant impact",
        "many users blocked",
        "users blocked",
        "unable to work",
        "production issue",
        "p2",
    ]

    for keyword in p2_keywords:
        if keyword in text_lower:
            return {
                "urgency": "P2",
                "reason": (
                    f"Major-impact signal detected: '{keyword}'. "
                    "The issue appears to affect normal operations."
                ),
            }

    # -----------------------------------------------------
    # P3 — moderate impact
    # -----------------------------------------------------

    p3_keywords = [
        "degraded",
        "workaround",
        "intermittent",
        "slow",
        "timeout",
        "timed out",
        "performance",
        "latency",
        "throughput",
        "degradation",
        "p3",
    ]

    for keyword in p3_keywords:
        if keyword in text_lower:
            return {
                "urgency": "P3",
                "reason": (
                    f"Moderate-impact signal detected: '{keyword}'. "
                    "A workaround or continued operation may be possible."
                ),
            }

    # -----------------------------------------------------
    # Default P4
    # -----------------------------------------------------

    return {
        "urgency": "P4",
        "reason": (
            "No strong P1/P2/P3 impact indicators were detected; "
            "classified as low urgency."
        ),
    }


# =========================================================
# Responder team
# =========================================================

def recommend_team(
    product: str,
    category: str,
) -> str:

    if category == "Billing":
        return "Billing / Account Management"

    if category == "Integration":
        return "Integrations Support"

    if category == "Performance":
        return "Technical Support / Performance Engineering"

    if category == "Data Loss":
        return "Technical Support / Data Engineering"

    if category == "Feature Request":
        return "Product / Technical Support"

    if category == "Onboarding":
        return "Customer Success / Onboarding"

    if category == "How-To":
        return "Technical Support"

    if category == "Bug":
        return "Technical Support / Engineering"

    return "Technical Support"


# =========================================================
# Draft first response
# =========================================================

def generate_first_response(
    product: str,
    category: str,
    urgency: str,
    matched_kb: Dict[str, Any] | None,
) -> str:

    if matched_kb:
        kb_sentence = (
            "Our knowledge base has a potentially relevant article "
            f"({matched_kb['source']}, section: "
            f"{matched_kb['section']})."
        )
    else:
        kb_sentence = (
            "We did not find a directly matching knowledge-base article "
            "for this issue."
        )

    return (
        f"Hi,\n\n"
        f"Thank you for reporting this {product} issue. "
        f"We have classified it as a {category} issue with {urgency} priority. "
        f"{kb_sentence} "
        f"Our support team will review the issue and the reported "
        f"environment details and follow up with the next troubleshooting "
        f"steps.\n\n"
        f"Best,\n"
        f"Support Team"
    )


# =========================================================
# Main triage function
# =========================================================

def triage_ticket(
    ticket: str | Dict[str, Any]
) -> Dict[str, Any]:

    # -----------------------------------------------------
    # Accept either raw text or dictionary
    # -----------------------------------------------------

    if isinstance(ticket, dict):

        subject = ticket.get("subject", "")
        body = ticket.get("body", "")

        text = f"{subject}\n{body}".strip()

    else:

        text = str(ticket).strip()

    if not text:
        raise ValueError("Ticket text cannot be empty.")

    # -----------------------------------------------------
    # Product
    # -----------------------------------------------------

    product = detect_product(text)

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------

    category = detect_category(text)

    # -----------------------------------------------------
    # Urgency
    # -----------------------------------------------------

    urgency_result = detect_urgency(text)

    urgency = urgency_result["urgency"]
    urgency_reason = urgency_result["reason"]

    # -----------------------------------------------------
    # RAG / Knowledge Base
    # -----------------------------------------------------

    kb_results = rag_service.search(
        text,
        top_k=3,
    )

    matched_kb = kb_results[0] if kb_results else None

    # -----------------------------------------------------
    # Responder team
    # -----------------------------------------------------

    responder_team = recommend_team(
        product,
        category,
    )

    # -----------------------------------------------------
    # Draft response
    # -----------------------------------------------------

    first_response = generate_first_response(
        product=product,
        category=category,
        urgency=urgency,
        matched_kb=matched_kb,
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {
        "product": product,
        "classification": category,
        "urgency": urgency,
        "urgency_reason": urgency_reason,
        "knowledge_base_match": matched_kb,
        "recommended_responder_team": responder_team,
        "draft_first_response": first_response,
    }