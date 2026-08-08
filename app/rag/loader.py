from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = BASE_DIR / "Knowledge-base"


def load_documents() -> list[dict[str, str]]:
    """
    Load all Markdown knowledge-base documents.

    Returns:
        [
            {
                "source": "products/analyticshub.md",
                "content": "..."
            }
        ]
    """

    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        return documents

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*.md"):

        relative_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)

        content = file_path.read_text(
            encoding="utf-8"
        )

        documents.append(
            {
                "source": str(relative_path).replace("\\", "/"),
                "content": content,
            }
        )

    return documents