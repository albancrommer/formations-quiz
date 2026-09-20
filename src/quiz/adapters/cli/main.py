"""Composition root and entrypoint: `quiz --file <path> --out <dir>`."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from quiz.adapters.cli.prompting import parse_answer_input
from quiz.adapters.identity_hostname.provider import HostnameIdentityProvider
from quiz.adapters.questions_aiken.parser import AikenParseError, parse_aiken
from quiz.adapters.results_localfile.sink import LocalFileResultSink
from quiz.domain.models import Question, Quiz
from quiz.domain.run_quiz import run_quiz


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quiz", description="Quiz de fin de demi-journee.")
    parser.add_argument("--file", required=True, type=Path, help="Fichier de questions (format Aiken).")
    parser.add_argument("--out", required=True, type=Path, help="Dossier de sortie des resultats.")
    return parser


def _ask_terminal(question: Question) -> frozenset[str]:
    print(f"\n{question.prompt}")
    for choice in question.choices:
        print(f"  {choice.label}) {choice.text}")

    while True:
        raw = input("Votre reponse (ex: A ou A,C) : ")
        try:
            return parse_answer_input(raw, question)
        except ValueError as exc:
            print(f"  ! {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    try:
        quiz_text = args.file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Erreur : impossible de lire {args.file}: {exc}", file=sys.stderr)
        return 1

    try:
        questions = parse_aiken(quiz_text)
    except AikenParseError as exc:
        print(f"Erreur de format dans {args.file}: {exc}", file=sys.stderr)
        return 1

    if not questions:
        print(f"Erreur : aucune question trouvee dans {args.file}", file=sys.stderr)
        return 1

    quiz = Quiz(id=args.file.stem, title=args.file.stem, questions=questions)

    identity = HostnameIdentityProvider()
    student = identity.resolve_student()
    print(f"Bonjour {student.display_name}, {len(quiz.questions)} question(s) a suivre.")

    attempt = run_quiz(
        quiz=quiz,
        student=student,
        answer_question=_ask_terminal,
        clock=datetime.now,
    )

    sink = LocalFileResultSink(output_dir=args.out)
    sink.save(attempt)

    print(f"\nScore : {attempt.score}/{attempt.total}")
    print(f"Resultat enregistre dans {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
