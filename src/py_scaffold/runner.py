"""Safe subprocess execution.

All external commands go through :class:`CommandRunner`. Rules:

- never ``shell=True`` — commands are argument lists (design §24, §40)
- output streams live to the terminal *and* is captured, so failures can
  include the command's own error output
- ``check=True`` (the default) raises :class:`CommandExecutionError`
"""

import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from py_scaffold.errors import CommandExecutionError

# How many trailing output lines to include in failure messages.
_ERROR_TAIL_LINES = 20


@dataclass(frozen=True)
class CommandResult:
    """Outcome of a finished command."""

    args: tuple[str, ...]
    returncode: int
    output: str  # combined stdout + stderr


class CommandRunner:
    """Runs external commands safely and predictably."""

    def run(
        self,
        command: Sequence[str],
        cwd: Path | None = None,
        check: bool = True,
        stream: bool = True,
    ) -> CommandResult:
        """Run ``command`` and return its result.

        ``stream=True`` tees combined output to the console while capturing
        it; ``stream=False`` runs silently (for output we parse, e.g.
        ``uv --version``). Raises :class:`CommandExecutionError` on non-zero
        exit when ``check`` is set.
        """
        argv = [str(part) for part in command]

        if stream:
            returncode, output = self._run_streaming(argv, cwd)
        else:
            completed = subprocess.run(
                argv,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            returncode = completed.returncode
            output = completed.stdout + completed.stderr

        result = CommandResult(args=tuple(argv), returncode=returncode, output=output)

        if check and returncode != 0:
            tail = "\n".join(output.splitlines()[-_ERROR_TAIL_LINES:])
            raise CommandExecutionError(
                argv,
                returncode,
                f"Command failed (exit {returncode}): {' '.join(argv)}\n{tail}",
            )
        return result

    @staticmethod
    def _run_streaming(argv: list[str], cwd: Path | None) -> tuple[int, str]:
        process = subprocess.Popen(  # noqa: S603 - argument list, never a shell
            argv,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        lines: list[str] = []
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            sys.stdout.flush()
            lines.append(line)
        return process.wait(), "".join(lines)
