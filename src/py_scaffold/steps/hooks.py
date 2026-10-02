"""prek configuration and Git hook installation (§19, §30)."""

from collections.abc import Callable
from importlib import resources

from py_scaffold.config import ProjectConfig
from py_scaffold.constants import SYMBOL_WARN
from py_scaffold.environment import EnvironmentStatus
from py_scaffold.errors import HookInstallationError
from py_scaffold.runner import CommandRunner


def write_prek_config(config: ProjectConfig) -> None:
    """Write ``prek.toml`` with local hooks running uv-managed tools."""
    template = (resources.files("py_scaffold") / "templates" / "prek.toml").read_text(
        encoding="utf-8"
    )
    (config.project_path / "prek.toml").write_text(template, encoding="utf-8")


def install_git_hooks(
    config: ProjectConfig,
    environment: EnvironmentStatus,
    runner: CommandRunner,
    out: Callable[[str], None] = print,
) -> None:
    """Install pre-commit hooks via prek.

    Hooks need a Git repository. If Git is unavailable we skip with a
    warning — the project works without hooks (§30). If the project is not
    a repo yet, we initialize one so hook installation succeeds.
    """
    if not environment.git_available:
        out(f"{SYMBOL_WARN} Git not found — skipping hook installation.")
        out("  Install Git and run: uv run prek install")
        return

    try:
        if not (config.project_path / ".git").exists():
            runner.run(["git", "init"], cwd=config.project_path, stream=False)
        runner.run(["uv", "run", "prek", "install"], cwd=config.project_path)
    except Exception as exc:
        raise HookInstallationError(
            "Failed to install Git hooks via prek.\n"
            "You can retry manually with: uv run prek install"
        ) from exc
