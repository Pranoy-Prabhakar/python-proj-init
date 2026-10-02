#!/usr/bin/env bash
# Bootstrap only (design §31): verify uv exists, then hand off to the
# Python CLI, which contains ALL project-generation logic.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: uv is not installed."
    echo
    echo "Install uv first:"
    echo
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo
    echo "After installation, rerun this script."
    exit 1
fi

exec uv run python-proj-init "$@"
