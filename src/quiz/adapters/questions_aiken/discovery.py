"""Discovers available Aiken quiz files in a directory, for the CLI's picker."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quiz.adapters.questions_aiken.parser import extract_formation, extract_session, extract_title

_SESSION_ORDER = {"matin": 0, "apres-midi": 1}


@dataclass(frozen=True)
class AvailableQuiz:
    path: Path
    title: str
    formation: str | None = None
    session: str | None = None


@dataclass(frozen=True)
class QuizGroup:
    formation: str | None
    quizzes: tuple[AvailableQuiz, ...]


def _session_sort_key(quiz: AvailableQuiz) -> tuple[int, str]:
    session = (quiz.session or "").lower()
    return (_SESSION_ORDER.get(session, len(_SESSION_ORDER)), quiz.path.name)


def discover_quizzes(questions_dir: Path) -> tuple[AvailableQuiz, ...]:
    if not questions_dir.is_dir():
        return ()

    quizzes = []
    for path in sorted(questions_dir.glob("*.aiken")):
        text = path.read_text(encoding="utf-8")
        title = extract_title(text) or path.stem
        quizzes.append(
            AvailableQuiz(
                path=path,
                title=title,
                formation=extract_formation(text),
                session=extract_session(text),
            )
        )

    quizzes.sort(key=lambda q: (q.formation or "", _session_sort_key(q)))
    return tuple(quizzes)


def group_quizzes(quizzes: tuple[AvailableQuiz, ...]) -> tuple[QuizGroup, ...]:
    groups: dict[str | None, list[AvailableQuiz]] = {}
    for quiz in quizzes:
        groups.setdefault(quiz.formation, []).append(quiz)

    return tuple(
        QuizGroup(formation=formation, quizzes=tuple(quizzes_in_group))
        for formation, quizzes_in_group in groups.items()
    )
