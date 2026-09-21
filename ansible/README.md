# ansible/albancrommer.formations_quiz

Reusable role that installs `formations-quiz` (the `quiz1`/`quiz2` CLI
commands) on a student VPS from the project's GitHub Releases:
https://github.com/albancrommer/formations-quiz/releases

It downloads the release tarball, extracts it, and runs the bundled
`install.sh` (same script used for manual deploys). Idempotent: re-running
against a host already on the target version does nothing.

## Usage

```bash
python3 -m venv .venv
.venv/bin/pip install ansible-core
.venv/bin/ansible-galaxy collection install -r requirements.yml

cp inventory.example.ini inventory.ini   # edit with your real hosts
.venv/bin/ansible-playbook -i inventory.ini site.yml
```

## Role variables

See `roles/albancrommer.formations_quiz/defaults/main.yml`. Notably:

- `formations_quiz_version` — `latest` (default) or a pinned tag (`v0.1.1`)
- `formations_quiz_results_dir` — where quiz results are written; defaults
  to `/home/{{ formations_quiz_student_user }}/quiz-results`. Not
  hardcoded — override per-inventory if the student account differs.
- `formations_quiz_student_user` — defaults to `stagiaire`

## Testing

The role has a [Molecule](https://ansible.readthedocs.io/projects/molecule/)
scenario (Docker driver) covering install, idempotence, and an end-to-end
quiz run:

```bash
python3 -m venv .venv
.venv/bin/pip install "ansible-core>=2.15" "molecule>=6.0" "molecule-plugins[docker]"
.venv/bin/ansible-galaxy collection install -r requirements.yml

cd roles/albancrommer.formations_quiz
PATH="../../.venv/bin:$PATH" molecule test
```
