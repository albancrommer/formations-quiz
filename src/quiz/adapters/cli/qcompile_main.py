"""qcompile: merges fetched quiz result files into one CSV report.

Usage:
    qcompile <results-dir> [--out report.csv]

Runs on the trainer's machine, not deployed to student VPS. Reads the
directory tree produced by `ansible/fetch_results.yml` (one subfolder
per host, each containing that host's *.yaml result files) or any
directory containing result YAML files, recursively.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from quiz.adapters.results_localfile.merge import collect_attempts, summarize_attempts

FIELDNAMES = ("student", "quiz_id", "attempts", "worst_score", "best_score", "total")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qcompile", description="Compile les resultats de quiz recuperes en un rapport CSV."
    )
    parser.add_argument("results_dir", type=Path, help="Dossier contenant les fichiers de resultats (*.yaml).")
    parser.add_argument("--out", type=Path, default=Path("report.csv"), help="Fichier CSV de sortie (defaut : report.csv).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    if not args.results_dir.is_dir():
        print(f"Erreur : dossier introuvable : {args.results_dir}", file=sys.stderr)
        return 1

    attempts = collect_attempts(args.results_dir)

    if not attempts:
        print(f"Erreur : aucun resultat trouve dans {args.results_dir}", file=sys.stderr)
        return 1

    rows = summarize_attempts(attempts)

    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "student": row.student,
                    "quiz_id": row.quiz_id,
                    "attempts": row.attempts,
                    "worst_score": row.worst_score if row.worst_score is not None else "",
                    "best_score": row.best_score,
                    "total": row.total,
                }
            )

    print(
        f"{len(attempts)} tentative(s), {len(rows)} combinaison(s) etudiant/quiz "
        f"compilees dans {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
