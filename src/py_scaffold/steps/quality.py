"""Ruff and ty configuration for generated projects (§17–18).

Both live in the generated project's ``pyproject.toml``. We append vetted
TOML blocks (the file's shape is known — we just ran ``uv init``) and verify
the result still parses with stdlib ``tomllib``.
"""

import tomllib
from pathlib import Path

from py_scaffold.config import ProjectConfig
from py_scaffold.errors import ValidationError

_RUFF_TEMPLATE = """
[tool.ruff]
line-length = 100
target-version = "{target_version}"
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
"""

# ty auto-detects a ./src layout; declaring it explicitly keeps behavior
# stable across layouts and documents intent (§18: sensible defaults only).
_TY_TEMPLATE = """
[tool.ty.environment]
root = ["./src"]
python-version = "{python_version}"
"""


def _target_version(python_version: str) -> str:
    """``3.12`` -> ``py312`` for Ruff's ``target-version``."""
    return "py" + python_version.strip().replace(".", "")


def _append_toml_block(pyproject: Path, block: str) -> None:
    """Append ``block`` and verify the whole file still parses as TOML."""
    content = pyproject.read_text(encoding="utf-8")
    updated = content.rstrip() + "\n" + block
    try:
        tomllib.loads(updated)
    except tomllib.TOMLDecodeError as exc:
        raise ValidationError(f"Generated pyproject.toml is invalid: {exc}") from exc
    pyproject.write_text(updated, encoding="utf-8")


def configure_ruff(config: ProjectConfig) -> None:
    pyproject = config.project_path / "pyproject.toml"
    _append_toml_block(
        pyproject,
        _RUFF_TEMPLATE.format(target_version=_target_version(config.python_version)),
    )


def configure_ty(config: ProjectConfig) -> None:
    pyproject = config.project_path / "pyproject.toml"
    _append_toml_block(
        pyproject,
        _TY_TEMPLATE.format(python_version=config.python_version),
    )
