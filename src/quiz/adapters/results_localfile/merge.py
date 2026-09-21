"""Merges many per-attempt result YAML files (fetched from several hosts)
into a flat list of rows, ready to write out as a report (e.g. CSV).

Malformed or incomplete files are skipped, not fatal: a single corrupt
result shouldn't block compiling everyone else's.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

_REQUIRED_FIELDS = ("quiz_id", "student", "score", "total", "started_at", "finished_at")


@dataclass(frozen=True)
class AttemptRow:
    student: str
    quiz_id: str
    score: int
    total: int
    started_at: str
    finished_at: str
    source_file: Path


def collect_attempts(results_dir: Path) -> list[AttemptRow]:
    rows: list[AttemptRow] = []

    for path in sorted(Path(results_dir).rglob("*.yaml")):
        row = _load_row(path)
        if row is not None:
            rows.append(row)

    rows.sort(key=lambda r: r.finished_at)
    return rows


def _load_row(path: Path) -> AttemptRow | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"! Fichier ignore (YAML invalide) : {path}: {exc}", file=sys.stderr)
        return None

    if not isinstance(data, dict) or not all(field in data for field in _REQUIRED_FIELDS):
        print(f"! Fichier ignore (champs manquants) : {path}", file=sys.stderr)
        return None

    return AttemptRow(
        student=data["student"],
        quiz_id=data["quiz_id"],
        score=data["score"],
        total=data["total"],
        started_at=str(data["started_at"]),
        finished_at=str(data["finished_at"]),
        source_file=path,
    )
