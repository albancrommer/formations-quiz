"""Persists a finished attempt as one YAML file per result.

No server, no database: the trainer collects these files manually
(scp, USB, shared folder) and merges them later.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from quiz.domain.models import Attempt

_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def _slug(value: str) -> str:
    return _SLUG_RE.sub("-", value.lower()).strip("-")


class LocalFileResultSink:
    def __init__(self, output_dir: Path) -> None:
        self._output_dir = Path(output_dir)

    def save(self, attempt: Attempt) -> None:
        self._output_dir.mkdir(parents=True, exist_ok=True)

        filename = (
            f"{attempt.finished_at:%Y%m%d-%H%M%S}"
            f"_{_slug(attempt.quiz_id)}"
            f"_{_slug(attempt.student.display_name)}.yaml"
        )
        payload = {
            "quiz_id": attempt.quiz_id,
            "student": attempt.student.display_name,
            "started_at": attempt.started_at.isoformat(),
            "finished_at": attempt.finished_at.isoformat(),
            "score": attempt.score,
            "total": attempt.total,
            "results": [
                {
                    "question_id": r.question_id,
                    "given": sorted(r.given_labels),
                    "correct": r.correct,
                }
                for r in attempt.results
            ],
        }

        path = self._output_dir / filename
        path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))
