#!/usr/bin/env bash
# Installs quiz-cli on a student VPS: venv under INSTALL_DIR, question files,
# and the quiz1/quiz2 wrapper commands in /usr/local/bin.
#
# Usage (as root, from an extracted tarball):
#   ./install.sh
#
# STDOUT reports what was installed; STDERR reports progress/errors.

set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/quiz-cli}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
RESULTS_DIR="${RESULTS_DIR:-/home/stagiaire/quiz-results}"
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
mkdir -p "$INSTALL_DIR/questions"
cp "$script_dir/questions/"*.aiken "$INSTALL_DIR/questions/"

echo "==> Preparation du dossier de resultats ($RESULTS_DIR)" >&2
mkdir -p "$RESULTS_DIR"
if id stagiaire &>/dev/null; then
    chown stagiaire:stagiaire "$RESULTS_DIR"
fi

write_wrapper() {
    local name="$1" quiz_file="$2"
    cat > "$BIN_DIR/$name" <<EOF
#!/bin/sh
exec "$INSTALL_DIR/venv/bin/quiz" --file "$INSTALL_DIR/questions/$quiz_file" --out "$RESULTS_DIR" "\$@"
EOF
    chmod +x "$BIN_DIR/$name"
    echo "==> Commande installee : $name" >&2
}

write_wrapper quiz1 k8s-bases-matin.aiken
write_wrapper quiz2 k8s-bases-apres-midi.aiken

echo "Installation terminee." >&2
echo "Commandes disponibles : quiz1 (K8s Bases matin), quiz2 (K8s Bases apres-midi)"
echo "Resultats enregistres dans : $RESULTS_DIR"
