"""Project generation pipeline (§13, §43).

Each step is a small function; this module only orchestrates them, reports
progress, and turns failures into a clear partial-project message (§29).
"""

from collections.abc import Callable

from py_scaffold.config import ProjectConfig
from py_scaffold.constants import SYMBOL_OK, SYMBOL_WARN
from py_scaffold.environment import EnvironmentChecker, require_uv
from py_scaffold.errors import ScaffoldError
from py_scaffold.profiles.base import get_profile
from py_scaffold.runner import CommandRunner
from py_scaffold.steps.dependencies import install_dev_dependencies
from py_scaffold.steps.hooks import install_git_hooks, write_prek_config
from py_scaffold.steps.makefile import generate_makefile
from py_scaffold.steps.project_init import (
    check_target_directory,
    create_virtual_environment,
    initialize_project,
    sync_dependencies,
)
from py_scaffold.steps.python_setup import ensure_python
from py_scaffold.steps.quality import configure_ruff, configure_ty
from py_scaffold.steps.readme import generate_readme
from py_scaffold.steps.validate import validate_generated_project


def create_project(
    config: ProjectConfig,
    runner: CommandRunner | None = None,
    out: Callable[[str], None] = print,
) -> None:
    """Create the project described by ``config``.

    Raises :class:`ScaffoldError` on any expected failure; the CLI turns it
    into a concise message and exit code 1.
    """
    runner = runner or CommandRunner()

    out("\nChecking environment...")
    environment = EnvironmentChecker(runner=runner).inspect()
    require_uv(environment)
    out(f"{SYMBOL_OK} uv {environment.uv_version or 'detected'}")
    if environment.git_available:
        out(f"{SYMBOL_OK} Git available")
    else:
        out(f"{SYMBOL_WARN} Git not found — hooks will be skipped")
    if environment.make_available:
        out(f"{SYMBOL_OK} Make detected")
    else:
        out(f"{SYMBOL_WARN} Make is not installed.")
        out("  The Makefile will still be generated.")
        out("  You can run the underlying uv commands directly.")

    profile = get_profile(config.project_type)

    steps: list[tuple[str, Callable[[], None]]] = [
        ("Input validated", lambda: check_target_directory(config)),
        (
            f"Python {config.python_version} available",
            lambda: ensure_python(config.python_version, runner),
        ),
        ("Project initialized", lambda: initialize_project(config, profile, runner)),
        ("Virtual environment created", lambda: create_virtual_environment(config, runner)),
        ("Dependencies synchronized", lambda: sync_dependencies(config, runner)),
        (
            "Development dependencies installed",
            lambda: install_dev_dependencies(config, runner),
        ),
        ("Ruff configured", lambda: configure_ruff(config)),
        ("ty configured", lambda: configure_ty(config)),
        ("prek configured", lambda: write_prek_config(config)),
    ]
    if config.install_hooks:
        steps.append(
            ("Git hooks installed", lambda: install_git_hooks(config, environment, runner, out))
        )
    if config.create_makefile:
        steps.append(("Makefile generated", lambda: generate_makefile(config)))
    steps += [
        ("README generated", lambda: generate_readme(config, profile)),
        ("Project validation passed", lambda: validate_generated_project(config, runner)),
    ]

    out("\nCreating project...")
    for label, step in steps:
        try:
            step()
        except ScaffoldError as exc:
            raise ScaffoldError(
                f"{exc}\n\n"
                "Project creation failed before completion.\n"
                f"Partial project may remain at:\n  {config.project_path}\n"
                "Fix the reported issue and rerun the command."
            ) from exc
        out(f"{SYMBOL_OK} {label}")

    out(f"\nProject created successfully:\n  {config.project_path}")
