"""Detection of external tools and the host operating system."""

import platform
import re
import shutil
from collections.abc import Callable
from dataclasses import dataclass

from py_scaffold.constants import UV_INSTALL_UNIX, UV_INSTALL_WINDOWS
from py_scaffold.errors import MissingUvError
from py_scaffold.runner import CommandRunner


@dataclass(frozen=True)
class EnvironmentStatus:
    """Snapshot of everything the generator needs from the host."""

    os: str  # "macos" | "windows" | "linux" | other, lowercased
    uv_available: bool
    uv_version: str | None
    git_available: bool
    make_available: bool


class EnvironmentChecker:
    """Inspects the host. Dependencies are injected for easy testing."""

    def __init__(
        self,
        runner: CommandRunner | None = None,
        which: Callable[[str], str | None] | None = None,
    ) -> None:
        self._runner = runner or CommandRunner()
        # Resolved at call time (not def time) so tests can monkeypatch
        # shutil.which and have it take effect.
        self._which = which or shutil.which

    def get_os(self) -> str:
        """Return a normalized OS name: ``macos``, ``windows`` or ``linux``."""
        system = platform.system().lower()
        return {"darwin": "macos"}.get(system, system)

    def check_uv(self) -> bool:
        return self._which("uv") is not None

    def check_git(self) -> bool:
        return self._which("git") is not None

    def check_make(self) -> bool:
        return self._which("make") is not None

    def uv_version(self) -> str | None:
        """Return the installed uv version, e.g. ``0.12.13``, or ``None``."""
        if not self.check_uv():
            return None
        result = self._runner.run(["uv", "--version"], check=False, stream=False)
        if result.returncode != 0:
            return None
        match = re.search(r"uv\s+(\S+)", result.output)
        return match.group(1) if match else None

    def inspect(self) -> EnvironmentStatus:
        """Collect the full environment snapshot (idempotent, §39)."""
        return EnvironmentStatus(
            os=self.get_os(),
            uv_available=self.check_uv(),
            uv_version=self.uv_version(),
            git_available=self.check_git(),
            make_available=self.check_make(),
        )


def require_uv(status: EnvironmentStatus) -> None:
    """Raise :class:`MissingUvError` with install guidance if uv is absent (§11).

    We never install uv silently — the user runs the official installer.
    """
    if status.uv_available:
        return
    install = UV_INSTALL_WINDOWS if status.os == "windows" else UV_INSTALL_UNIX
    raise MissingUvError(
        "uv is not installed.\n\n"
        f"Install it first:\n\n  {install}\n\n"
        "After installation, rerun this command."
    )
