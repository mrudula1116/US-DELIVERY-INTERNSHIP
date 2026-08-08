from typing import Any


def chunk_documents(
    documents: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """
    Split knowledge-base documents into chunks.

    The provided DATA_SCHEMA recommends splitting
    on horizontal rules.
    """

    chunks = []

    for document in documents:

        source = document["source"]
        content = document["content"]

        sections = content.split("---")

        for index, section in enumerate(sections):

            section = section.strip()

            if not section:
                continue

            lines = section.splitlines()

            heading = None

            for line in lines:
                if line.startswith("#"):
                    heading = line.lstrip("#").strip()
                    break

            chunks.append(
                {
                    "chunk_id": f"{source}::chunk-{index}",
                    "source": source,
                    "section": heading,
                    "content": section,
                }
            )

    return chunks