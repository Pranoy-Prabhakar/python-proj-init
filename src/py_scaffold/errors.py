"""Domain-specific exceptions for python-proj-init.

The CLI catches :class:`ScaffoldError` and prints a concise, user-facing
message without a stack trace. Anything else is treated as a bug.
"""


class ScaffoldError(Exception):
    """Base class for all expected, user-facing scaffold failures."""


class MissingUvError(ScaffoldError):
    """uv is not installed or not on PATH."""


class InvalidProjectNameError(ScaffoldError):
    """The requested project name is not valid."""


class TargetDirectoryExistsError(ScaffoldError):
    """The target directory already exists and is not empty."""


class PythonInstallationError(ScaffoldError):
    """uv could not find or install the requested Python version."""


class CommandExecutionError(ScaffoldError):
    """An external command exited non-zero.

    Carries the argument list and exit code so callers can report exactly
    which command failed (design §27, §29).
    """

    def __init__(self, command: list[str], returncode: int, message: str) -> None:
        super().__init__(message)
        # NB: do not name this ``args`` — that would shadow ``Exception.args``
        # and replace the message in ``str(exc)``.
        self.command = command
        self.returncode = returncode


class ProjectInitializationError(ScaffoldError):
    """uv init failed."""


class DependencyInstallationError(ScaffoldError):
    """Installing development dependencies failed."""


class HookInstallationError(ScaffoldError):
    """Installing Git hooks via prek failed."""


class ValidationError(ScaffoldError):
    """Post-generation project validation failed."""
