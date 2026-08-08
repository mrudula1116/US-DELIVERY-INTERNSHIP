from typing import Any


def generate_answer(
    question: str,
    results: list[dict[str, Any]],
) -> tuple[str, list[dict[str, str | None]]]:

    if not results:

        return (
            "I could not find relevant information in the "
            "provided knowledge base. Please create a support "
            "ticket for further assistance.",
            [],
        )

    best = results[0]

    content = best["content"]

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    # Prefer numbered troubleshooting steps.
    steps = [
        line
        for line in lines
        if len(line) > 2
        and line[0].isdigit()
        and line[1] in "."
    ]

    if steps:

        answer = (
            "Based on the knowledge base, the recommended "
            "troubleshooting steps are:\n\n"
            + "\n".join(
                f"{index + 1}. {step.split('.', 1)[1].strip()}"
                for index, step in enumerate(steps[:5])
            )
        )

    else:

        useful_lines = [
            line
            for line in lines
            if not line.startswith("#")
        ]

        answer = (
            "According to the knowledge base:\n\n"
            + "\n".join(useful_lines[:8])
        )

    citations = []

    seen = set()

    for result in results:

        key = (
            result["source"],
            result.get("section"),
        )

        if key in seen:
            continue

        seen.add(key)

        citations.append(
            {
                "source": result["source"],
                "section": result.get("section"),
            }
        )

    return answer, citations