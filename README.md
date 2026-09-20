# quiz-cli

CLI quiz engine for post-half-day comprehension checks (theory + practice questions),
built for Uptime Formation's DevOps training modules.

Status: working CLI (Aiken question format, hostname-based identity, local YAML results).
Web delivery and content beyond the sample quiz are not built yet.

## Architecture

Hexagonal. `src/quiz/domain/` holds entities and ports with zero I/O.
Adapters implement the ports:

- `adapters/questions_aiken/` — reads quizzes written in [Aiken format](https://docs.moodle.org/en/Aiken_format)
- `adapters/identity_hostname/` — resolves the student's identity (CLI: from hostname; prompts as fallback)
- `adapters/results_localfile/` — writes one YAML result file per attempt
- `adapters/cli/` — command-line entrypoint

Other question formats (GIFT, IMS QTI) or delivery channels (web) can be added
as new adapters without touching the domain.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Usage

```bash
quiz --file sample_questions/sample_quiz.aiken --out ~/quiz-results
```

The student is asked each question in turn (theory and practice mixed),
answers with a letter or comma-separated letters for multi-select
(`A` or `A,C`), and sees their score at the end. The result is written as
one YAML file per attempt in `--out`, named
`<timestamp>_<quiz>_<student>.yaml`.

Identity is inferred from the machine hostname (first label, e.g. `sacha`
from `sacha.brx2022.uptime-formation.fr`); if the hostname looks generic
(`localhost`, etc.) the student is prompted for their name instead.

### Question format

Questions are written in [Aiken format](https://docs.moodle.org/en/Aiken_format),
with two extensions:

- Multi-select: `ANSWER: A,B` instead of a single letter.
- Question kind: an optional `%kind: theory` or `%kind: practice` line
  before the question text (defaults to `theory`).

See `sample_questions/sample_quiz.aiken` for a full example.
