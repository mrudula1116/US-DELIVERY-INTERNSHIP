from pathlib import Path
import re
from typing import List, Dict


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge-base"


# ---------------------------------------------------------
# Knowledge Base Loading
# ---------------------------------------------------------

def load_documents() -> List[Dict]:
    """
    Load all Markdown documents from knowledge-base/.

    Each major section separated by --- becomes a document chunk.
    """

    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}"
        )

    for path in KNOWLEDGE_BASE_DIR.rglob("*.md"):

        content = path.read_text(
            encoding="utf-8"
        )

        # Split documents on horizontal rules
        sections = re.split(
            r"\n---\s*\n",
            content
        )

        for section in sections:

            section = section.strip()

            if not section:
                continue

            # Find first Markdown heading
            heading_match = re.search(
                r"^#{1,6}\s+(.+)$",
                section,
                re.MULTILINE
            )

            if heading_match:
                heading = heading_match.group(1).strip()
            else:
                heading = path.stem

            documents.append(
                {
                    "source": str(
                        path.relative_to(BASE_DIR)
                    ),
                    "section": heading,
                    "content": section,
                }
            )

    return documents


# ---------------------------------------------------------
# Simple Retrieval
# ---------------------------------------------------------

def search_knowledge_base(
    query: str,
    top_k: int = 3
) -> List[Dict]:
    """
    Retrieve relevant knowledge-base chunks.

    Ranking strategy:
    1. Exact phrase matches
    2. Heading matches
    3. Content matches
    4. Product-specific relevance
    5. Topic/file-specific relevance
    6. Penalize unrelated documents
    """

    documents = load_documents()

    query_lower = query.lower().strip()

    query_terms = [
        word.lower()
        for word in re.findall(r"\b\w+\b", query_lower)
        if len(word) > 2
    ]

    results = []

    # ---------------------------------------------------------
    # Topic detection
    # ---------------------------------------------------------

    auth_terms = {
        "authentication",
        "auth",
        "sso",
        "saml",
        "login",
        "signin",
        "sign",
        "token",
        "scope",
        "scopes",
        "session",
        "group",
        "idp",
        "identity",
        "403",
        "forbidden",
    }

    performance_terms = {
        "performance",
        "slow",
        "slowness",
        "timeout",
        "timed",
        "latency",
        "throughput",
        "slowly",
        "degradation",
    }

    integration_terms = {
        "integration",
        "salesforce",
        "snowflake",
        "webhook",
        "oauth",
        "api",
    }

    query_is_auth = bool(
        set(query_terms) & auth_terms
    )

    query_is_performance = bool(
        set(query_terms) & performance_terms
    )

    query_is_integration = bool(
        set(query_terms) & integration_terms
    )

    # ---------------------------------------------------------
    # Product detection
    # ---------------------------------------------------------

    products = [
        "analyticshub",
        "databridge",
        "cloudsync",
        "securevault",
        "workflowengine",
    ]

    detected_products = [
        product
        for product in products
        if product in query_lower
    ]

    # ---------------------------------------------------------
    # Score documents
    # ---------------------------------------------------------

    for document in documents:

        section = document["section"].lower()
        content = document["content"].lower()
        source = document["source"].lower()

        score = 0

        # -----------------------------------------------------
        # 1. Exact query phrase
        # -----------------------------------------------------

        if query_lower in content:
           score += 30

        if query_lower in section:
            score += 50

        # -----------------------------------------------------
        # 2. Individual query terms
        # -----------------------------------------------------

        for term in query_terms:

            # Heading match
            if term in section:
                score += 8

            # Content match
            if term in content:
                score += 2

            # Filename match
            if term in source:
                score += 5

        # -----------------------------------------------------
        # 3. Product relevance
        # -----------------------------------------------------

        for product in detected_products:

            if product in source:
                score += 15

            if product in section:
                score += 8

            if product in content:
                score += 3

        # -----------------------------------------------------
        # 4. Authentication / SSO relevance
        # -----------------------------------------------------

        if query_is_auth:

            # VERY strong preference for authentication guide
            if "authentication-sso.md" in source:
                score += 40

            # Authentication-related sections
            if any(
                keyword in section
                for keyword in [
                    "authentication",
                    "sso",
                    "service account",
                    "scope",
                    "concurrent session",
                ]
            ):
                score += 20

            # Authentication terminology
            auth_matches = sum(
                1
                for term in auth_terms
                if term in content
            )

            score += min(auth_matches * 2, 15)

            # Penalize unrelated integration documents
            if (
                "performance-integrations.md" in source
                and "authentication-sso.md" not in source
            ):
                score -= 15

        # -----------------------------------------------------
        # 5. Performance relevance
        # -----------------------------------------------------

        if query_is_performance:

            if "performance-integrations.md" in source:
                score += 30

            if any(
                keyword in section
                for keyword in [
                    "performance",
                    "dashboard timeout",
                    "throughput",
                    "slow",
                ]
            ):
                score += 15

        # -----------------------------------------------------
        # 6. Integration relevance
        # -----------------------------------------------------

        if query_is_integration:

            if "performance-integrations.md" in source:
                score += 10

            if any(
                keyword in section
                for keyword in [
                    "salesforce",
                    "snowflake",
                    "integration",
                    "webhook",
                ]
            ):
                score += 10

        # -----------------------------------------------------
        # 7. SecureVault authentication
        # -----------------------------------------------------

        if "securevault" in query_lower:

            if "securevault.md" in source:
                score += 20

        # -----------------------------------------------------
        # 8. CloudSync authentication
        # -----------------------------------------------------

        if "cloudsync" in query_lower:

            if "cloudsync.md" in source:
                score += 20

        # -----------------------------------------------------
        # Keep relevant documents only
        # -----------------------------------------------------

        if score > 0:

            result = document.copy()

            result["score"] = score

            results.append(result)

    # ---------------------------------------------------------
    # Sort by relevance
    # ---------------------------------------------------------

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]
# ---------------------------------------------------------
# RAG Service
# ---------------------------------------------------------

class RAGService:
    """
    Retrieval service used by the application.

    Usage:

        rag_service.search(
            "AnalyticsHub dashboard timeout",
            3
        )
    """

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:

        return search_knowledge_base(
            query=query,
            top_k=top_k
        )


# ---------------------------------------------------------
# Public service instance
# ---------------------------------------------------------

rag_service = RAGService()