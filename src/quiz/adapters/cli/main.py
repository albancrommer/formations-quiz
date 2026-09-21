"""Composition root and entrypoint.

Default usage (student-friendly): `quiz` alone lists the available quizzes
found in --questions-dir and lets the student pick one.
Power-user usage: `quiz --file <path> --out <dir>` skips the picker.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from quiz.adapters.cli.prompting import parse_answer_input
from quiz.adapters.identity_hostname.provider import HostnameIdentityProvider
from quiz.adapters.questions_aiken.discovery import AvailableQuiz, discover_quizzes
from quiz.adapters.questions_aiken.parser import AikenParseError, extract_title, parse_aiken
from quiz.adapters.results_localfile.sink import LocalFileResultSink
from quiz.domain.models import Question, Quiz
from quiz.domain.review import review_attempt
from quiz.domain.run_quiz import run_quiz

DEFAULT_QUESTIONS_DIR = Path("/opt/quiz-cli/questions")
DEFAULT_RESULTS_DIR = Path("/home/stagiaire/quiz-results")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quiz", description="Quiz de fin de demi-journee.")
    parser.add_argument(
        "--file", type=Path, default=None, help="Fichier de questions (format Aiken). Sans ce flag, une liste est proposee."
    )
    parser.add_argument(
        "--questions-dir",
        type=Path,
        default=DEFAULT_QUESTIONS_DIR,
        help=f"Dossier ou chercher les quiz disponibles (defaut : {DEFAULT_QUESTIONS_DIR}).",
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_RESULTS_DIR, help=f"Dossier de sortie des resultats (defaut : {DEFAULT_RESULTS_DIR})."
    )
    return parser


def _choose_quiz(available: tuple[AvailableQuiz, ...]) -> Path | None:
    print("\n=== Quiz disponibles ===")
    for i, quiz in enumerate(available, start=1):
        print(f"  {i}) {quiz.title}")
    print()

    while True:
        raw = input(f"Choisissez un quiz (1-{len(available)}) : ").strip()
        try:
            choice = int(raw)
        except ValueError:
            print("  ! Entrez un numero.", file=sys.stderr)
            continue
        if 1 <= choice <= len(available):
            return available[choice - 1].path
        print(f"  ! Choisissez un numero entre 1 et {len(available)}.", file=sys.stderr)


def _make_terminal_asker(total: int) -> Callable[[Question], frozenset[str]]:
    position = 0

    def ask(question: Question) -> frozenset[str]:
        nonlocal position
        position += 1

        print(f"\n--- Question {position}/{total} ---")
        print(question.prompt)
        for choice in question.choices:
            print(f"  {choice.label}) {choice.text}")

        while True:
            raw = input("Votre reponse (ex: A ou A,C) : ")
            try:
                return parse_answer_input(raw, question)
            except ValueError as exc:
                print(f"  ! {exc}", file=sys.stderr)

    return ask


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    identity = HostnameIdentityProvider()
    student = identity.resolve_student()
    print(f"Bonjour {student.display_name} !")

    quiz_file = args.file
    if quiz_file is None:
        available = discover_quizzes(args.questions_dir)
        if not available:
            print(f"Erreur : aucun quiz trouve dans {args.questions_dir}", file=sys.stderr)
            return 1
        quiz_file = _choose_quiz(available)

    try:
        quiz_text = quiz_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Erreur : impossible de lire {quiz_file}: {exc}", file=sys.stderr)
        return 1

    try:
        questions = parse_aiken(quiz_text)
    except AikenParseError as exc:
        print(f"Erreur de format dans {quiz_file}: {exc}", file=sys.stderr)
        return 1

    if not questions:
        print(f"Erreur : aucune question trouvee dans {quiz_file}", file=sys.stderr)
        return 1

    title = extract_title(quiz_text) or quiz_file.stem
    quiz = Quiz(id=quiz_file.stem, title=title, questions=questions)

    print(f"\n=== {quiz.title} ===")
    print(f"{len(quiz.questions)} question(s) a suivre.")

    attempt = run_quiz(
        quiz=quiz,
        student=student,
        answer_question=_make_terminal_asker(len(quiz.questions)),
        clock=datetime.now,
    )

    sink = LocalFileResultSink(output_dir=args.out)
    sink.save(attempt)

    print("\n=== Resultat ===")
    print(f"Score : {attempt.score}/{attempt.total}")

    review = review_attempt(quiz, attempt.results)
    if review.wrong_positions:
        positions = ", ".join(str(p) for p in review.wrong_positions)
        print(f"\nVoici les questions sur lesquelles vous vous etes trompe(e) : {positions}")

        reponse = input("Voir les bonnes reponses ? (o/N) : ").strip().lower()
        if reponse in ("o", "oui", "y", "yes"):
            for item in review.wrong_items:
                correct = ", ".join(f"{c.label}) {c.text}" for c in item.correct_choices)
                print(f"\nQ{item.position} : {item.prompt}")
                print(f"  Bonne reponse : {correct}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
