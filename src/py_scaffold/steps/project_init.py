"""Project initialization, virtualenv creation, and dependency sync (§13–15)."""

from py_scaffold.config import ProjectConfig
from py_scaffold.errors import ProjectInitializationError, TargetDirectoryExistsError
from py_scaffold.profiles.base import ProjectProfile
from py_scaffold.runner import CommandRunner


def check_target_directory(config: ProjectConfig) -> None:
    """Refuse to touch an existing non-empty directory (§28).

    Safe beats convenient: we never delete or overwrite user files.
    """
    path = config.project_path
    if path.exists() and any(path.iterdir()):
        raise TargetDirectoryExistsError(
            f"Target directory already exists and is not empty:\n  {path}"
        )


def initialize_project(
    config: ProjectConfig,
    profile: ProjectProfile,
    runner: CommandRunner,
) -> None:
    """Run ``uv init`` for the configured profile, creating the project dir."""
    # The destination itself may not exist yet (e.g. --path /tmp/new-dir);
    # create it so uv init has a valid working directory.
    config.destination.mkdir(parents=True, exist_ok=True)
    try:
        runner.run(profile.init_command(config), cwd=config.destination)
    except Exception as exc:
        raise ProjectInitializationError(
            f"Project initialization failed for {config.name!r}."
        ) from exc


def create_virtual_environment(config: ProjectConfig, runner: CommandRunner) -> None:
    """Create ``.venv`` explicitly (§15)."""
    try:
        runner.run(["uv", "venv"], cwd=config.project_path)
    except Exception as exc:
        raise ProjectInitializationError("Failed to create the virtual environment.") from exc


def sync_dependencies(config: ProjectConfig, runner: CommandRunner) -> None:
    """Synchronize the environment from the lockfile."""
    try:
        runner.run(["uv", "sync"], cwd=config.project_path)
    except Exception as exc:
        raise ProjectInitializationError("Dependency synchronization failed.") from exc
