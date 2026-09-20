# quiz-cli

CLI quiz engine for post-half-day comprehension checks (theory + practice questions),
built for Uptime Formation's DevOps training modules.

Status: early scaffold, domain layer only. No working CLI yet.

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

Not yet implemented.
