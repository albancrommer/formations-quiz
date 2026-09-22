# Changelog
## [0.7.0] - 2026-09-22

### Features

- Add fetch_results.yml playbook to pull quiz results off VPS

- Group quiz picker by formation, order matin before apres-midi


## [0.6.0] - 2026-09-21

### Chore

- Update CHANGELOG.md for v0.6.0


### Features

- Add qcompile, merges fetched quiz results into one CSV report


## [0.5.0] - 2026-09-21

### Chore

- Update CHANGELOG.md for v0.5.0


### Features

- Replace quiz1/quiz2 wrappers with one friendly quiz command


## [0.4.0] - 2026-09-21

### Chore

- Update CHANGELOG.md for v0.4.0


### Features

- Add K8s Dev quiz content for both half-days


## [0.3.0] - 2026-09-21

### Chore

- Update CHANGELOG.md for v0.3.0


### Features

- Show wrong answers after the quiz, offer to reveal correct ones


## [0.2.0] - 2026-09-21

### Chore

- Update CHANGELOG.md for v0.2.0


### Features

- Add reusable ansible role for VPS deployment


## [0.1.1] - 2026-09-20

### Bug Fixes

- Switch to CI-driven auto-versioning, fix release notes bug

- Truncate changelog entries to the commit subject line


### Chore

- Update CHANGELOG.md for v0.1.0

- Update CHANGELOG.md for v0.1.1


## [0.1.0] - 2026-09-20

### Build

- Package quiz1/quiz2 for VPS deploy, fix hostname identity rule


### CI

- Add tag-triggered release workflow with git-cliff changelog


### Documentation

- Document usage, add K8s Bases quiz content for both half-days


### Features

- Scaffold hexagonal quiz engine (Aiken parser, CLI, local-file results)


