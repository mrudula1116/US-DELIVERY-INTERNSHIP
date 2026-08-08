import re
from collections import Counter
from typing import Any


STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "to",
    "for",
    "of",
    "and",
    "or",
    "in",
    "on",
    "with",
    "how",
    "what",
    "why",
    "can",
    "i",
    "we",
    "my",
    "our",
    "do",
    "does",
    "it",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())

    return [
        word
        for word in words
        if word not in STOP_WORDS
    ]


def score_chunk(
    query_tokens: list[str],
    content: str,
) -> float:

    content_tokens = tokenize(content)

    if not content_tokens:
        return 0.0

    counts = Counter(content_tokens)

    score = 0.0

    for token in query_tokens:

        if token in counts:

            score += 1

            # Extra weight for exact repeated terms
            score += min(counts[token] - 1, 3) * 0.2

    return score


def retrieve(
    query: str,
    chunks: list[dict[str, Any]],
    top_k: int = 3,
) -> list[dict[str, Any]]:

    query_tokens = tokenize(query)

    scored_chunks = []

    for chunk in chunks:

        score = score_chunk(
            query_tokens,
            chunk["content"],
        )

        if score > 0:

            scored_chunks.append(
                {
                    **chunk,
                    "score": score,
                }
            )

    scored_chunks.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_chunks[:top_k]