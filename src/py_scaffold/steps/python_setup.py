"""Ensure the requested Python version exists, via uv (design §12).

uv manages Python for us — no OS-specific install logic here.
"""

from py_scaffold.errors import PythonInstallationError
from py_scaffold.runner import CommandRunner


def ensure_python(version: str, runner: CommandRunner) -> None:
    """Make ``version`` available, installing it through uv if needed."""
    found = runner.run(["uv", "python", "find", version], check=False, stream=False)
    if found.returncode == 0:
        return

    try:
        runner.run(["uv", "python", "install", version])
    except Exception as exc:
        raise PythonInstallationError(
            f"Unable to install Python {version} using uv.\n\n"
            f"Command:\n  uv python install {version}\n\n"
            "Run the command manually for more details."
        ) from exc
