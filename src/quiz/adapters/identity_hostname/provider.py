"""Identity adapter: infers the student's name from the machine hostname.

Rule (best-effort, flagged for trainer review): take the first label of the
hostname (before the first dot), title-case it. This fits VPS names like
"sacha.brx2022.uptime-formation.fr" -> "Sacha". Falls back to an interactive
prompt when the hostname is empty or looks generic (localhost, etc.) so it
never silently mislabels a result.
"""

from __future__ import annotations

import socket
from collections.abc import Callable

from quiz.domain.models import Student

GENERIC_HOSTNAMES = frozenset({"localhost", "127", "debian", "ubuntu"})


def _default_prompt() -> str:
    return input("Nom et prenom : ").strip()


class HostnameIdentityProvider:
    def __init__(
        self,
        hostname_fn: Callable[[], str] = socket.gethostname,
        prompt_fn: Callable[[], str] = _default_prompt,
    ) -> None:
        self._hostname_fn = hostname_fn
        self._prompt_fn = prompt_fn

    def resolve_student(self) -> Student:
        hostname = self._hostname_fn().strip()
        first_label = hostname.split(".")[0] if hostname else ""

        if not first_label or first_label.lower() in GENERIC_HOSTNAMES:
            return Student(display_name=self._prompt_fn())

        return Student(display_name=first_label.title())
