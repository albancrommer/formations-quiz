#!/usr/bin/env bash
# Builds a self-contained tarball: wheel + install.sh + quiz content.
# Usage: packaging/build_tarball.sh
# Output: dist/quiz-cli-deploy.tar.gz

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

echo "==> Building wheel"
if [[ -x "$repo_root/.venv/bin/python3" ]]; then
    build_python="$repo_root/.venv/bin/python3"
else
    build_python="python3"
fi
"$build_python" -m pip install --quiet --upgrade build >&2
"$build_python" -m build --wheel --outdir "$stage/wheel" . >&2

echo "==> Staging package"
mkdir -p "$stage/questions"
cp sample_questions/k8s-bases-matin.aiken "$stage/questions/"
cp sample_questions/k8s-bases-apres-midi.aiken "$stage/questions/"
cp sample_questions/k8s-dev-matin.aiken "$stage/questions/"
cp sample_questions/k8s-dev-apres-midi.aiken "$stage/questions/"
cp packaging/install.sh "$stage/install.sh"
chmod +x "$stage/install.sh"

mkdir -p dist
tar -C "$stage" -czf dist/quiz-cli-deploy.tar.gz wheel questions install.sh

echo "==> Built dist/quiz-cli-deploy.tar.gz" >&2
