# quiz-cli

CLI quiz engine for post-half-day comprehension checks (theory + practice questions),
built for Uptime Formation's DevOps training modules.

Status: working CLI, deployed to student VPS via Ansible/GitHub Releases.
Web delivery is not built yet.

## Architecture

Hexagonal. `src/quiz/domain/` holds entities and ports with zero I/O.
Adapters implement the ports:

- `adapters/questions_aiken/` — reads quizzes written in [Aiken format](https://docs.moodle.org/en/Aiken_format), plus quiz discovery for the picker
- `adapters/identity_hostname/` — resolves the student's identity (CLI: from hostname; prompts as fallback)
- `adapters/results_localfile/` — writes one YAML result file per attempt, and merges many back into a report
- `adapters/cli/` — two command-line entrypoints: `quiz` (student-facing) and `qcompile` (trainer-facing)

Other question formats (GIFT, IMS QTI) or delivery channels (web) can be added
as new adapters without touching the domain.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Usage: `quiz` (student-facing)

Deployed on student VPS as a single `quiz` command (see `ansible/` and
`packaging/`). Run with no arguments, it lists the available quizzes and
lets the student pick one:

```bash
quiz
```

```
Bonjour Sacha !

=== Quiz disponibles ===
  1) K8s Bases - Matin
  2) K8s Bases - Apres-midi
  ...
Choisissez un quiz (1-4) :
```

Each question is answered with a letter or comma-separated letters for
multi-select (`A` or `A,C`). At the end, the score is shown; wrong answers
are always listed by number, with an offer to reveal the correct ones.

Power-user / scripting form, bypassing the picker:

```bash
quiz --file sample_questions/k8s-bases-matin.aiken --out ~/quiz-results
```

The result is written as one YAML file per attempt in `--out`, named
`<timestamp>_<quiz>_<student>.yaml`.

Identity is inferred from the machine hostname: `vnc-server-<name>` (current
VPS naming) or the first dotted label (legacy naming). If the hostname looks
generic (`localhost`, etc.) the student is prompted for their name instead.

### Question format

Questions are written in [Aiken format](https://docs.moodle.org/en/Aiken_format),
with these extensions:

- Multi-select: `ANSWER: A,B` instead of a single letter.
- Question kind: an optional `%kind: theory` or `%kind: practice` line
  before the question text (defaults to `theory`).
- File-level markers, each before the first question:
  - `%title: <text>` — friendly display name for the picker (falls back
    to the filename otherwise).
  - `%formation: <text>` — groups quizzes together in the picker, shown
    as a `--- <formation> ---` header.
  - `%session: matin|apres-midi` — orders quizzes within a formation
    (matin before apres-midi; anything else sorts after both).

See `sample_questions/k8s-bases-matin.aiken` for a full example.

## Usage: `qcompile` (trainer-facing)

After fetching result files from student VPS (see `ansible/fetch_results.yml`),
compile them into one CSV report:

```bash
qcompile <results-dir> [--out report.csv]
```

Recursively finds every `*.yaml` result file under `<results-dir>` (works
whether they're flat or organized in per-host subfolders), skips malformed
or incomplete files with a warning on stderr, and writes one CSV row per
**student × quiz** (not per attempt — retakes are collapsed): `student`,
`quiz_id`, `attempts`, `worst_score`, `best_score`, `total`. `worst_score`
is left empty when there's only one attempt (nothing to be "worst" of).
