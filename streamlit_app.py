import streamlit as st
import json
from pathlib import Path
import sys

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "Data"
KB_DIR = ROOT / "Knowledge-base"

ACCOUNTS_FILE = DATA_DIR / "accounts.json"
TICKETS_FILE = DATA_DIR / "tickets.json"


# ============================================================
# BACKEND IMPORTS
# ============================================================

try:
    from app.services.triage_service import triage_ticket
    TRIAGE_AVAILABLE = True
except Exception as e:
    TRIAGE_AVAILABLE = False
    TRIAGE_ERROR = str(e)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="US Delivery Support System",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        background: #f4f7fb;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    .title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #17233d;
        margin-bottom: 0;
    }

    .subtitle {
        color: #687791;
        margin-bottom: 1.5rem;
    }

    .card {
        background: white;
        padding: 1.4rem;
        border-radius: 14px;
        border: 1px solid #e3e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(24,39,75,.06);
    }

    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #e3e8f0;
        text-align: center;
    }

    .metric-label {
        color: #738098;
        font-size: .8rem;
    }

    .metric-value {
        color: #17233d;
        font-size: 1.5rem;
        font-weight: 800;
    }

    .priority {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 7px;
        font-weight: 800;
        font-size: .8rem;
    }

    .p1 {
        background: #ffe5e8;
        color: #c9273b;
    }

    .p2 {
        background: #fff0d8;
        color: #b56b00;
    }

    .p3 {
        background: #e8f1ff;
        color: #2864e8;
    }

    .p4 {
        background: #e9f7ef;
        color: #168450;
    }

    .result-title {
        color: #18253f;
        font-size: 1.15rem;
        font-weight: 750;
    }

    .small-text {
        color: #6d7a90;
        font-size: .85rem;
    }

    .success-box {
        background: #e9f7ef;
        border: 1px solid #ccebd9;
        padding: 12px;
        border-radius: 8px;
        color: #168450;
    }

    .info-box {
        background: #eef4ff;
        border: 1px solid #d6e3ff;
        padding: 12px;
        border-radius: 8px;
        color: #2864e8;
    }

    .risk-box {
        background: #fff8ec;
        border: 1px solid #f1dfbc;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    section[data-testid="stSidebar"] {
        background: #101827;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA HELPERS
# ============================================================

@st.cache_data
def load_json(path):
    if not path.exists():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def normalize_list(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["accounts", "tickets", "data", "items", "results"]:
            if key in data and isinstance(data[key], list):
                return data[key]

    return []


accounts = normalize_list(load_json(ACCOUNTS_FILE))
tickets = normalize_list(load_json(TICKETS_FILE))


# ============================================================
# KNOWLEDGE BASE
# ============================================================

@st.cache_data
def load_knowledge_base():
    documents = []

    if not KB_DIR.exists():
        return documents

    for path in KB_DIR.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")

            documents.append(
                {
                    "name": path.name,
                    "path": str(path.relative_to(ROOT)),
                    "text": text,
                }
            )
        except Exception:
            pass

    return documents


kb_documents = load_knowledge_base()


def simple_kb_search(query, limit=5):
    query_words = {
        word.lower()
        for word in query.split()
        if len(word) > 2
    }

    scored = []

    for doc in kb_documents:
        text = doc["text"].lower()

        score = sum(
            1 for word in query_words
            if word in text
        )

        if score > 0:
            scored.append((score, doc))

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [doc for _, doc in scored[:limit]]


# ============================================================
# ACCOUNT SEARCH
# ============================================================

def find_account(account_id):
    target = str(account_id).strip().lower()

    if not target:
        return None

    for account in accounts:
        values = [
            account.get("id"),
            account.get("account_id"),
            account.get("accountId"),
            account.get("name"),
            account.get("customer"),
            account.get("customer_name"),
        ]

        for value in values:
            if value is not None and str(value).lower() == target:
                return account

    return None


def account_tickets(account):
    account_id = str(
        account.get("id")
        or account.get("account_id")
        or account.get("accountId")
        or ""
    ).lower()

    name = str(
        account.get("name")
        or account.get("customer")
        or account.get("customer_name")
        or ""
    ).lower()

    results = []

    for ticket in tickets:
        text = json.dumps(ticket).lower()

        if account_id and account_id in text:
            results.append(ticket)
        elif name and name in text:
            results.append(ticket)

    return results


def make_account_brief(account, related_tickets):
    name = (
        account.get("name")
        or account.get("customer")
        or account.get("customer_name")
        or "Customer Account"
    )

    status = (
        account.get("status")
        or account.get("health")
        or account.get("health_status")
        or "Unknown"
    )

    industry = account.get("industry", "Not specified")

    risk_tickets = []

    risk_words = [
        "churn",
        "cancel",
        "cancellation",
        "escalat",
        "unhappy",
        "critical",
        "urgent",
        "renewal",
        "downtime",
        "lost",
        "blocked",
    ]

    for ticket in related_tickets:
        text = json.dumps(ticket).lower()

        if any(word in text for word in risk_words):
            risk_tickets.append(ticket)

    summary = (
        f"{name} currently has an account status of {status}. "
        f"The account operates in {industry}. "
        f"{len(related_tickets)} related support ticket(s) were found "
        f"in the available dataset. "
        f"{len(risk_tickets)} ticket(s) contain potential escalation "
        f"or churn-risk signals."
    )

    talking_points = [
        f"Review current account health: {status}.",
        f"Discuss the {len(related_tickets)} available support ticket(s).",
        "Confirm whether any unresolved technical issues require escalation.",
        "Review upcoming customer priorities and required support actions.",
    ]

    return {
        "name": name,
        "status": status,
        "industry": industry,
        "summary": summary,
        "risk_tickets": risk_tickets,
        "talking_points": talking_points,
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="font-size:22px;font-weight:800;">
        🇺🇸 US Delivery
        </div>
        <div style="color:#9aa8bd;">
        Support System
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🎫 Ticket Triage",
            "👤 Accounts",
            "🔎 Tickets",
            "📚 Knowledge Base",
        ],
    )

    st.divider()

    st.caption(
        "Production Support AI\n"
        "Tasks 1–2 + RAG"
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.markdown(
        '<div class="title">US Delivery Support System</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "AI-assisted support operations for Technical Support and TAM teams."
        "</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Tickets</div>
                <div class="metric-value">{len(tickets)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Accounts</div>
                <div class="metric-value">{len(accounts)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">KB Documents</div>
                <div class="metric-value">{len(kb_documents)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        status = "Online" if TRIAGE_AVAILABLE else "Error"

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Triage Engine</div>
                <div class="metric-value">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    st.markdown(
        """
        <div class="card">
        <h3>What this system does</h3>
        <p>
        The platform helps Technical Support engineers triage incoming
        tickets and helps TAMs prepare customer account health briefs.
        It also retrieves relevant product knowledge from the supplied
        Markdown knowledge base.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("🎫 **Task 1**\n\nTicket classification, priority, routing and KB matching.")

    with col2:
        st.info("👤 **Task 2**\n\nAccount health, risks, evidence and TAM talking points.")

    with col3:
        st.info("📚 **RAG**\n\nSearches the supplied product documentation.")


# ============================================================
# TASK 1 — TRIAGE
# ============================================================

elif page == "🎫 Ticket Triage":

    st.title("🎫 Intelligent Ticket Triage")

    st.caption(
        "Classify, prioritise, route and enrich an incoming support ticket."
    )

    subject = st.text_input(
        "Ticket Subject",
        placeholder="Example: Payment processing failing",
    )

    body = st.text_area(
        "Support Ticket",
        height=180,
        placeholder=(
            "Example: Customers are unable to process payments "
            "after yesterday's deployment..."
        ),
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        run = st.button(
            "🚀 Run AI Triage",
            type="primary",
            use_container_width=True,
        )

    with col2:
        clear = st.button(
            "Clear",
            use_container_width=True,
        )

    if clear:
        st.rerun()

    if run:

        if not subject.strip() and not body.strip():
            st.warning("Please enter a ticket subject or ticket body.")

        elif not TRIAGE_AVAILABLE:
            st.error("Triage service could not be imported.")

            with st.expander("Technical error"):
                st.code(TRIAGE_ERROR)

        else:

            with st.spinner("Running ticket triage..."):

                try:
                    result = triage_ticket(
                        {
                            "subject": subject,
                            "body": body,
                        }
                    )

                    st.session_state["triage_result"] = result

                except Exception as e:
                    st.error(f"Triage failed: {e}")

    result = st.session_state.get("triage_result")

    if result:

        st.divider()

        st.subheader("Triage Result")

        priority = result.get("urgency", "P4")
        priority_class = priority.lower()

        st.markdown(
            f"""
            <span class="priority {priority_class}">
            {priority}
            </span>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Product Area",
                result.get("product", "Unknown"),
            )

        with c2:
            st.metric(
                "Issue Category",
                result.get("classification", "Unknown"),
            )

        with c3:
            st.metric(
                "Responder Team",
                result.get(
                    "recommended_responder_team",
                    "Technical Support",
                ),
            )

        st.markdown("### Why this priority?")

        st.info(
            result.get(
                "urgency_reason",
                "No urgency reasoning available.",
            )
        )

        kb = result.get("knowledge_base_match")

        st.markdown("### Knowledge Base Match")

        if kb:

            if isinstance(kb, dict):

                st.success(
                    f"Matched document: "
                    f"{kb.get('source', kb.get('path', 'Knowledge Base'))}"
                )

                if kb.get("section"):
                    st.write(
                        f"**Section:** {kb['section']}"
                    )

                if kb.get("content"):
                    st.write(kb["content"])

                if kb.get("text"):
                    st.write(kb["text"])

            else:
                st.success(str(kb))

        else:
            st.warning(
                "No directly matching knowledge-base article was found."
            )

        st.markdown("### Draft First Response")

        response = result.get(
            "draft_first_response",
            "No response generated.",
        )

        st.text_area(
            "Support response",
            value=response,
            height=180,
        )


# ============================================================
# TASK 2 — ACCOUNTS
# ============================================================

elif page == "👤 Accounts":

    st.title("👤 TAM Account Health")

    st.caption(
        "Generate an actionable account brief from the supplied customer data."
    )

    account_id = st.text_input(
        "Account ID",
        placeholder="Example: ACC-3847",
    )

    if st.button(
        "Generate Account Brief",
        type="primary",
    ):

        if not account_id.strip():
            st.warning("Enter an account ID.")

        else:

            account = find_account(account_id)

            if not account:
                st.error(
                    f"Account '{account_id}' was not found."
                )

            else:

                related = account_tickets(account)

                brief = make_account_brief(
                    account,
                    related,
                )

                st.success(
                    f"Account found: {brief['name']}"
                )

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Account Status",
                        brief["status"],
                    )

                with c2:
                    st.metric(
                        "Related Tickets",
                        len(related),
                    )

                with c3:
                    st.metric(
                        "Potential Risks",
                        len(brief["risk_tickets"]),
                    )

                st.markdown("### Executive Summary")

                st.write(brief["summary"])

                st.markdown("### Open Risks & Flagged Issues")

                if brief["risk_tickets"]:

                    for i, ticket in enumerate(
                        brief["risk_tickets"],
                        1,
                    ):

                        ticket_text = (
                            ticket.get("body")
                            or ticket.get("description")
                            or ticket.get("subject")
                            or json.dumps(ticket)
                        )

                        st.markdown(
                            f"""
                            <div class="risk-box">
                            <b>Risk {i}</b><br>
                            {ticket_text[:700]}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                else:

                    st.success(
                        "No obvious escalation or churn-risk signals "
                        "were detected using the available dataset."
                    )

                st.markdown("### Recommended TAM Talking Points")

                for point in brief["talking_points"]:
                    st.write(f"• {point}")

                st.markdown("### Account Data")

                with st.expander("View source account data"):
                    st.json(account)


# ============================================================
# TICKETS
# ============================================================

elif page == "🔎 Tickets":

    st.title("🔎 Support Tickets")

    query = st.text_input(
        "Search tickets",
        placeholder="Search by ID, customer, subject or issue...",
    )

    if query:

        query_lower = query.lower()

        matches = []

        for ticket in tickets:

            text = json.dumps(ticket).lower()

            if query_lower in text:
                matches.append(ticket)

        st.write(
            f"Found **{len(matches)}** matching ticket(s)."
        )

        for ticket in matches[:50]:

            ticket_id = (
                ticket.get("id")
                or ticket.get("ticket_id")
                or ticket.get("ticketId")
                or "Ticket"
            )

            subject = (
                ticket.get("subject")
                or ticket.get("title")
                or "Support Ticket"
            )

            body = (
                ticket.get("body")
                or ticket.get("description")
                or ticket.get("issue")
                or ""
            )

            with st.expander(
                f"{ticket_id} — {subject}"
            ):

                st.write(body)

                st.json(ticket)

    else:

        st.info(
            "Enter a search term to inspect ticket history."
        )


# ============================================================
# KNOWLEDGE BASE
# ============================================================

elif page == "📚 Knowledge Base":

    st.title("📚 Knowledge Base")

    st.caption(
        "Search the supplied product and troubleshooting documentation."
    )

    query = st.text_input(
        "Knowledge Base Search",
        placeholder="Example: SSO authentication timeout",
    )

    if st.button(
        "Search Knowledge Base",
        type="primary",
    ):

        if not query.strip():
            st.warning("Enter a search query.")

        else:

            results = simple_kb_search(
                query,
                limit=5,
            )

            if results:

                st.success(
                    f"{len(results)} relevant document(s) found."
                )

                for doc in results:

                    with st.expander(
                        f"📄 {doc['name']}"
                    ):

                        st.caption(doc["path"])

                        st.markdown(
                            doc["text"][:5000]
                        )

            else:

                st.warning(
                    "No matching documentation was found."
                )

    st.divider()

    st.subheader("Retrieval Workflow")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.info("1️⃣ Ticket Input\n\nRaw support request")

    with c2:
        st.info("2️⃣ Retrieval\n\nSearch documentation")

    with c3:
        st.info("3️⃣ Known Issue\n\nMatch relevant article")

    with c4:
        st.info("4️⃣ Response\n\nRecommend action")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "US Delivery Support System • "
    "Task 1 Ticket Triage • "
    "Task 2 TAM Account Health • "
    "RAG Knowledge Retrieval"
)
