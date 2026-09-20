"""Domain entities for the quiz engine. No I/O here."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QuestionKind(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"


@dataclass(frozen=True)
class Choice:
    label: str  # e.g. "A", "B"
    text: str


@dataclass(frozen=True)
class Question:
    id: str
    prompt: str
    choices: tuple[Choice, ...]
    correct_labels: frozenset[str]
    kind: QuestionKind = QuestionKind.THEORY

    def is_correct(self, given_labels: frozenset[str]) -> bool:
        return given_labels == self.correct_labels


@dataclass(frozen=True)
class Quiz:
    id: str
    title: str
    questions: tuple[Question, ...]


@dataclass(frozen=True)
class Student:
    display_name: str


@dataclass(frozen=True)
class QuestionResult:
    question_id: str
    given_labels: frozenset[str]
    correct: bool


@dataclass(frozen=True)
class Attempt:
    quiz_id: str
    student: Student
    results: tuple[QuestionResult, ...]
    started_at: datetime
    finished_at: datetime

    @property
    def score(self) -> int:
        return sum(1 for r in self.results if r.correct)

    @property
    def total(self) -> int:
        return len(self.results)
