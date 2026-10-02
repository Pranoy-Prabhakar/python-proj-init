"""Post-generation validation (§33).

A generated project only counts as successful if these checks pass.
"""

from py_scaffold.config import ProjectConfig, ProjectType
from py_scaffold.errors import ValidationError
from py_scaffold.runner import CommandRunner


def validate_generated_project(config: ProjectConfig, runner: CommandRunner) -> None:
    """Run lint, type check, and (for libraries) a full build."""
    checks: list[tuple[str, list[str]]] = [
        ("uv sync", ["uv", "sync"]),
        ("ruff check", ["uv", "run", "ruff", "check", "."]),
        ("ty check", ["uv", "run", "ty", "check"]),
    ]
    if config.project_type is ProjectType.LIBRARY:
        checks.append(("uv build", ["uv", "build"]))

    for label, command in checks:
        try:
            runner.run(command, cwd=config.project_path)
        except Exception as exc:
            raise ValidationError(
                f"Project validation failed during: {label}\n"
                f"Fix the issue inside {config.project_path} and rerun the command."
            ) from exc
