"""Discovers available Aiken quiz files in a directory, for the CLI's picker."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quiz.adapters.questions_aiken.parser import extract_title


@dataclass(frozen=True)
class AvailableQuiz:
    path: Path
    title: str


def discover_quizzes(questions_dir: Path) -> tuple[AvailableQuiz, ...]:
    if not questions_dir.is_dir():
        return ()

    quizzes = []
    for path in sorted(questions_dir.glob("*.aiken")):
        title = extract_title(path.read_text(encoding="utf-8")) or path.stem
        quizzes.append(AvailableQuiz(path=path, title=title))

    return tuple(quizzes)
