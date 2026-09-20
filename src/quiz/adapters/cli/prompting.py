"""Parses raw terminal input into the label set a Question expects."""

from __future__ import annotations

from quiz.domain.models import Question


def parse_answer_input(raw: str, question: Question) -> frozenset[str]:
    labels = frozenset(part.strip().upper() for part in raw.split(","))

    if not raw.strip() or "" in labels:
        raise ValueError("Reponse vide.")

    valid = {c.label for c in question.choices}
    unknown = labels - valid
    if unknown:
        raise ValueError(f"Reponse(s) invalide(s) : {', '.join(sorted(unknown))}")

    return labels
