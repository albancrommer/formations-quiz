"""Parser for an Aiken-format quiz file.

Standard Aiken: question line, lettered choice lines ("A) ..."), then
"ANSWER: <letter>", questions separated by a blank line.

Extensions used here (documented, not standard Aiken):
- "ANSWER: A,B" for multi-select.
- An optional leading "%kind: theory|practice" comment line per question,
  defaulting to theory when absent.
"""

from __future__ import annotations

import re

from quiz.domain.models import Choice, Question, QuestionKind

_CHOICE_RE = re.compile(r"^([A-Z])\)\s*(.+)$")
_ANSWER_RE = re.compile(r"^ANSWER:\s*(.+)$", re.IGNORECASE)
_KIND_RE = re.compile(r"^%kind:\s*(\w+)\s*$", re.IGNORECASE)


class AikenParseError(ValueError):
    pass


def parse_aiken(text: str) -> tuple[Question, ...]:
    blocks = _split_blocks(text)
    return tuple(
        _parse_block(block, index) for index, block in enumerate(blocks, start=1)
    )


def _split_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _parse_block(lines: list[str], index: int) -> Question:
    kind = QuestionKind.THEORY
    if lines and (kind_match := _KIND_RE.match(lines[0])):
        kind = QuestionKind(kind_match.group(1).lower())
        lines = lines[1:]

    if not lines:
        raise AikenParseError(f"Question {index}: empty block")

    prompt, *rest = lines

    choices: list[Choice] = []
    answer_line: str | None = None
    for line in rest:
        if choice_match := _CHOICE_RE.match(line):
            choices.append(Choice(choice_match.group(1), choice_match.group(2)))
        elif answer_match := _ANSWER_RE.match(line):
            answer_line = answer_match.group(1)
        else:
            raise AikenParseError(f"Question {index}: unrecognized line {line!r}")

    if answer_line is None:
        raise AikenParseError(f"Question {index}: missing ANSWER line")
    if not choices:
        raise AikenParseError(f"Question {index}: no choices found")

    valid_labels = {c.label for c in choices}
    correct_labels = frozenset(label.strip() for label in answer_line.split(","))
    unknown = correct_labels - valid_labels
    if unknown:
        raise AikenParseError(
            f"Question {index}: ANSWER references unknown label(s) {sorted(unknown)}"
        )

    return Question(
        id=f"q{index}",
        prompt=prompt,
        choices=tuple(choices),
        correct_labels=correct_labels,
        kind=kind,
    )
