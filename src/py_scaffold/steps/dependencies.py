"""Install development dependencies into the generated project (§16)."""

from py_scaffold.config import ProjectConfig
from py_scaffold.constants import DEV_DEPENDENCIES
from py_scaffold.errors import DependencyInstallationError
from py_scaffold.runner import CommandRunner


def install_dev_dependencies(config: ProjectConfig, runner: CommandRunner) -> None:
    """Add ruff, ty and prek as dev dependencies (never runtime deps)."""
    try:
        runner.run(
            ["uv", "add", "--dev", *DEV_DEPENDENCIES],
            cwd=config.project_path,
        )
    except Exception as exc:
        raise DependencyInstallationError(
            f"Failed to install development dependencies: {', '.join(DEV_DEPENDENCIES)}"
        ) from exc
