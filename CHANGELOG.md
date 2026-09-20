# Changelog
## [0.1.0] - 2026-09-20

### Build

- 📦 build: package quiz1/quiz2 for VPS deploy, fix hostname identity rule

Real student VPS hostnames are "vnc-server-<name>", not the dotted
FQDN pattern assumed earlier — confirmed against a live box
(alban.kube.rackform.eu). HostnameIdentityProvider now strips that
prefix first, falling back to the legacy dotted-label rule.

Added packaging/build_tarball.sh (wheel + install.sh + K8s Bases
question files into one tarball) and packaging/install.sh, which
installs into /opt/quiz-cli, self-heals a missing python3-venv
package via apt, and writes quiz1/quiz2 wrappers into
/usr/local/bin pointing --out at /home/stagiaire/quiz-results.
Reinstalling now forces a clean venv instead of silently keeping
stale code when the version string is unchanged.

Also dropped the invalid SPDX license field from pyproject.toml
(setuptools warning; no real license decision made yet).

Verified end-to-end on alban.kube.rackform.eu: build, upload,
install, quiz1 and quiz2 both run and score correctly with zero
flags.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


### Documentation

- 📝 docs: document usage, add K8s Bases quiz content for both half-days

README now shows real `quiz --file --out` usage instead of "not yet
implemented". Added 6-question quizzes for K8s Bases matin and
apres-midi, drafted from docs/4_Kubernetes_Bases/ course+TP content
and reviewed with the trainer before committing.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


### Features

- ✨ feat: scaffold hexagonal quiz engine (Aiken parser, CLI, local-file results)

Domain layer (Question/Quiz/Attempt/Student, run_quiz use case) has zero
I/O. Three adapters implement the ports: Aiken-format question parser
(with documented multi-select and %kind: extensions), hostname-based
identity resolution with interactive fallback, and local YAML result
files. CLI entrypoint wires them via `quiz --file <path> --out <dir>`.

26 tests, TDD red-green throughout. Proven end-to-end against
sample_questions/sample_quiz.aiken with simulated terminal input.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


### Other

- 👷 ci: add tag-triggered release workflow with git-cliff changelog

Pushing a vX.Y.Z tag builds the release tarball (packaging/build_tarball.sh),
generates CHANGELOG.md from Conventional Commits via git-cliff, commits it
back to main, and publishes a GitHub Release with the tarball attached and
the tag's changelog section as release notes.

cliff.toml maps our gitmoji+conventional commit prefixes (feat/fix/docs/
build/refactor/test/chore) to changelog sections.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


