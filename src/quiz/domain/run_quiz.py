"""Use case: run a quiz end-to-end and build the resulting Attempt.

Stays I/O-free: `answer_question` and `clock` are injected callables so
adapters (CLI prompts, a future web handler) decide how answers are
actually collected, while this module only orchestrates and scores.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from quiz.domain.models import Attempt, Question, QuestionResult, Quiz, Student

AnswerQuestion = Callable[[Question], frozenset[str]]
Clock = Callable[[], datetime]


def run_quiz(
    *,
    quiz: Quiz,
    student: Student,
    answer_question: AnswerQuestion,
    clock: Clock,
) -> Attempt:
    started_at = clock()

    results = tuple(
        QuestionResult(
            question_id=question.id,
            given_labels=(given := answer_question(question)),
            correct=question.is_correct(given),
        )
        for question in quiz.questions
    )

    finished_at = clock()

    return Attempt(
        quiz_id=quiz.id,
        student=student,
        results=results,
        started_at=started_at,
        finished_at=finished_at,
    )
