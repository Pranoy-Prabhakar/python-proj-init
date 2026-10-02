"""Command-line interface for python-proj-init.

Structure:

- :func:`build_parser` — pure argparse setup (§7, §37)
- :func:`collect_config` — turns parsed args + interactive prompts into a
  validated :class:`ProjectConfig` (§8, §9)
- :func:`main` — wires everything together and maps expected
  :class:`ScaffoldError` failures to a clean message + exit code 1 (§27)

``input`` is injectable so tests can drive the interactive flow without a TTY.
"""

import argparse
from collections.abc import Callable
from pathlib import Path

from py_scaffold.config import ProjectConfig, ProjectType
from py_scaffold.constants import DEFAULT_PROJECT_TYPE, DEFAULT_PYTHON_VERSION, SYMBOL_ERROR
from py_scaffold.errors import ScaffoldError
from py_scaffold.generator import create_project
from py_scaffold.validation import (
    derive_distribution_name,
    derive_package_name,
    validate_project_name,
)

PROJECT_TYPES = [ProjectType.APPLICATION, ProjectType.LIBRARY]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python-proj-init",
        description="Cross-platform Python project scaffolder powered by uv.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    new = subparsers.add_parser("new", help="Create a new Python project.")
    new.add_argument("name", nargs="?", help="Project name, e.g. payment-utils")
    new.add_argument(
        "--type",
        choices=[t.value for t in PROJECT_TYPES],
        default=None,
        help=f"Project type (default: {DEFAULT_PROJECT_TYPE})",
    )
    new.add_argument(
        "--python",
        default=None,
        metavar="VERSION",
        help=f"Python version for the project (default: {DEFAULT_PYTHON_VERSION})",
    )
    new.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Destination directory (default: current directory)",
    )
    new.add_argument("--no-make", action="store_true", help="Do not generate a Makefile")
    new.add_argument("--no-hooks", action="store_true", help="Do not install Git hooks")
    new.add_argument(
        "--non-interactive",
        action="store_true",
        help="Never prompt; fail if required arguments are missing",
    )
    new.add_argument(
        "--force",
        action="store_true",
        help="Reserved: allow scaffolding into an existing empty directory",
    )
    return parser


def _prompt(
    message: str,
    default: str,
    input_fn: Callable[[str], str],
) -> str:
    """Ask for a value, falling back to ``default`` on empty input."""
    answer = input_fn(f"{message} [{default}]: ").strip()
    return answer or default


def _prompt_project_type(input_fn: Callable[[str], str], out: Callable[[str], None]) -> ProjectType:
    out("\nProject type:")
    for index, project_type in enumerate(PROJECT_TYPES, start=1):
        out(f"{index}. {project_type.value}")
    answer = input_fn(f"\nSelect project type [1-{len(PROJECT_TYPES)}, default 1]: ").strip()
    if not answer:
        return PROJECT_TYPES[0]
    if answer.isdigit() and 1 <= int(answer) <= len(PROJECT_TYPES):
        return PROJECT_TYPES[int(answer) - 1]
    lowered = answer.lower()
    for project_type in PROJECT_TYPES:
        if project_type.value == lowered:
            return project_type
    raise ScaffoldError(f"Invalid project type selection: {answer!r}")


def collect_config(
    args: argparse.Namespace,
    input_fn: Callable[[str], str] = input,
    out: Callable[[str], None] = print,
) -> ProjectConfig:
    """Resolve CLI args + prompts into a validated :class:`ProjectConfig`.

    Interactive mode prompts for anything missing; ``--non-interactive``
    requires a name argument and uses defaults for the rest (§8).
    """
    interactive = not args.non_interactive

    name = args.name
    if name is None:
        if not interactive:
            raise ScaffoldError("Project name is required in non-interactive mode.")
        name = input_fn("Project name: ").strip()
    validate_project_name(name)

    if args.type is not None:
        project_type = ProjectType(args.type)
    elif interactive:
        project_type = _prompt_project_type(input_fn, out)
    else:
        project_type = ProjectType(DEFAULT_PROJECT_TYPE)

    if args.python is not None:
        python_version = args.python
    elif interactive:
        python_version = _prompt("Python version", DEFAULT_PYTHON_VERSION, input_fn)
    else:
        python_version = DEFAULT_PYTHON_VERSION

    destination = (args.path or Path.cwd()).expanduser().resolve()

    return ProjectConfig(
        name=derive_distribution_name(name),
        package_name=derive_package_name(name),
        project_type=project_type,
        python_version=python_version,
        destination=destination,
        create_makefile=not args.no_make,
        install_hooks=not args.no_hooks,
    )


def main(
    argv: list[str] | None = None,
    input_fn: Callable[[str], str] = input,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "new":
        try:
            config = collect_config(args, input_fn=input_fn)
            create_project(config)
        except ScaffoldError as exc:
            print(f"{SYMBOL_ERROR} {exc}")
            return 1
        return 0

    return 0
