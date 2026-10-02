"""Shared constants for python-proj-init."""

import sys

DEFAULT_PYTHON_VERSION = "3.12"
DEFAULT_PROJECT_TYPE = "application"

UV_INSTALL_UNIX = "curl -LsSf https://astral.sh/uv/install.sh | sh"
UV_INSTALL_WINDOWS = (
    'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
)

# Terminal status symbols, with ASCII fallback for terminals that cannot
# render Unicode (e.g. some legacy Windows consoles).
_SUPPORTS_UNICODE = sys.stdout.encoding and "utf" in sys.stdout.encoding.lower()
SYMBOL_OK = "✓" if _SUPPORTS_UNICODE else "[OK]"
SYMBOL_WARN = "⚠" if _SUPPORTS_UNICODE else "[WARN]"
SYMBOL_ERROR = "✗" if _SUPPORTS_UNICODE else "[ERROR]"

# Development tools added to every generated project.
DEV_DEPENDENCIES = ["ruff", "ty", "prek"]
