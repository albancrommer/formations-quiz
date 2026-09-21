"""Post-quiz review: which questions were wrong, and their correct answers."""

from __future__ import annotations

from dataclasses import dataclass

from quiz.domain.models import Choice, QuestionResult, Quiz


@dataclass(frozen=True)
class WrongAnswer:
    position: int
    prompt: str
    correct_choices: tuple[Choice, ...]


@dataclass(frozen=True)
class Review:
    wrong_positions: tuple[int, ...]
    wrong_items: tuple[WrongAnswer, ...]


def review_attempt(quiz: Quiz, results: tuple[QuestionResult, ...]) -> Review:
    questions_by_id = {q.id: q for q in quiz.questions}

    wrong_items = tuple(
        WrongAnswer(
            position=position,
            prompt=questions_by_id[result.question_id].prompt,
            correct_choices=tuple(
                c
                for c in questions_by_id[result.question_id].choices
                if c.label in questions_by_id[result.question_id].correct_labels
            ),
        )
        for position, result in enumerate(results, start=1)
        if not result.correct
    )

    return Review(
        wrong_positions=tuple(item.position for item in wrong_items),
        wrong_items=wrong_items,
    )
