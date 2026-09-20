"""Hexagonal ports: abstract boundaries the domain depends on.

Adapters (CLI, Aiken parser, hostname identity, local-file results, ...)
implement these. The domain never imports an adapter.
"""

from __future__ import annotations

from typing import Protocol

from quiz.domain.models import Attempt, Quiz, Student


class QuestionSource(Protocol):
    """Loads a quiz's questions from some format (Aiken, GIFT, QTI, ...)."""

    def load_quiz(self, quiz_id: str) -> Quiz: ...


class IdentityProvider(Protocol):
    """Resolves who is taking the quiz."""

    def resolve_student(self) -> Student: ...


class ResultSink(Protocol):
    """Persists a finished attempt."""

    def save(self, attempt: Attempt) -> None: ...
