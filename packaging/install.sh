#!/usr/bin/env bash
# Installs quiz-cli on a student VPS: venv under INSTALL_DIR, question files,
# and the `quiz` wrapper command in BIN_DIR.
#
# Usage (as root, from an extracted tarball):
#   ./install.sh
#
# STDOUT reports what was installed; STDERR reports progress/errors.

set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/quiz-cli}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
RESULTS_DIR="${RESULTS_DIR:-/home/stagiaire/quiz-results}"
STUDENT_USER="${STUDENT_USER:-stagiaire}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -u)" -ne 0 ]]; then
    echo "Erreur : ce script doit etre execute en root (sudo ./install.sh)." >&2
    exit 1
fi

if [[ ! -d "$script_dir/wheel" ]] || [[ ! -d "$script_dir/questions" ]]; then
    echo "Erreur : archive incomplete, dossier 'wheel' ou 'questions' introuvable." >&2
    exit 1
fi

ensure_venv_module() {
    if python3 -m venv --help >/dev/null 2>&1; then
        local probe
        probe="$(mktemp -d)"
        if python3 -m venv "$probe/check" >/dev/null 2>&1; then
            rm -rf "$probe"
            return 0
        fi
        rm -rf "$probe"
    fi

    if ! command -v apt-get >/dev/null 2>&1; then
        echo "Erreur : le module 'venv' de python3 est indisponible et apt-get est introuvable pour l'installer." >&2
        return 1
    fi

    local py_version pkg
    py_version="$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
    pkg="python${py_version}-venv"

    echo "==> Installation du paquet manquant : $pkg" >&2
    apt-get update -qq >&2
    apt-get install -y -qq "$pkg" >&2
}

echo "==> Installation dans $INSTALL_DIR" >&2
ensure_venv_module
mkdir -p "$INSTALL_DIR"
rm -rf "$INSTALL_DIR/venv"
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip >&2
"$INSTALL_DIR/venv/bin/pip" install --quiet --force-reinstall "$script_dir"/wheel/*.whl >&2

echo "==> Copie des questions" >&2
install -d "$INSTALL_DIR/questions"
install -m 0644 -t "$INSTALL_DIR/questions" "$script_dir"/questions/*.aiken

echo "==> Preparation du dossier de resultats ($RESULTS_DIR)" >&2
mkdir -p "$RESULTS_DIR"
if id "$STUDENT_USER" &>/dev/null; then
    chown "$STUDENT_USER:$STUDENT_USER" "$RESULTS_DIR"
fi

quiz_wrapper="$(mktemp)"
trap 'rm -f "$quiz_wrapper"' EXIT
cat > "$quiz_wrapper" <<EOF
#!/bin/sh
exec "$INSTALL_DIR/venv/bin/quiz" --questions-dir "$INSTALL_DIR/questions" --out "$RESULTS_DIR" "\$@"
EOF
install -m 0755 "$quiz_wrapper" "$BIN_DIR/quiz"

echo "Installation terminee." >&2
echo "Commande disponible : quiz"
echo "Resultats enregistres dans : $RESULTS_DIR"
