"""Identity adapter: infers the student's name from the machine hostname.

Rule (best-effort, flagged for trainer review), tried in order:
1. Current VPS naming: "vnc-server-<name>" -> "<Name>" (prefix stripped).
2. Legacy naming: "<name>.domain..." -> first dotted label, title-cased.
Falls back to an interactive prompt when the hostname is empty or looks
generic (localhost, etc.) so it never silently mislabels a result.
"""

from __future__ import annotations

import socket
from collections.abc import Callable

from quiz.domain.models import Student

GENERIC_HOSTNAMES = frozenset({"localhost", "127", "debian", "ubuntu"})
_VNC_SERVER_PREFIX = "vnc-server-"


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

        if hostname.lower().startswith(_VNC_SERVER_PREFIX):
            name = hostname[len(_VNC_SERVER_PREFIX):]
        else:
            name = hostname.split(".")[0] if hostname else ""

        if not name or name.lower() in GENERIC_HOSTNAMES:
            return Student(display_name=self._prompt_fn())

        return Student(display_name=name.title())
