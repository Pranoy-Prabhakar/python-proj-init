"""Unit tests for CommandRunner."""

import sys
from dataclasses import FrozenInstanceError

import pytest

from py_scaffold.errors import CommandExecutionError
from py_scaffold.runner import CommandResult, CommandRunner


def py_cmd(code: str) -> list[str]:
    """A command that runs ``code`` with the current interpreter."""
    return [sys.executable, "-c", code]


class TestRun:
    def test_success_captures_output(self) -> None:
        result = CommandRunner().run(py_cmd("print('hello')"), stream=False)
        assert result.returncode == 0
        assert "hello" in result.output
        assert result.args[0] == sys.executable

    def test_check_true_raises_on_failure(self) -> None:
        with pytest.raises(CommandExecutionError) as exc_info:
            CommandRunner().run(py_cmd("import sys; sys.exit(3)"), stream=False)
        assert exc_info.value.returncode == 3
        assert "exit 3" in str(exc_info.value)

    def test_check_false_returns_failure(self) -> None:
        result = CommandRunner().run(py_cmd("import sys; sys.exit(3)"), check=False, stream=False)
        assert result.returncode == 3

    def test_failure_message_includes_output_tail(self) -> None:
        code = "print('fatal detail'); import sys; sys.exit(1)"
        with pytest.raises(CommandExecutionError) as exc_info:
            CommandRunner().run(py_cmd(code), stream=False)
        assert "fatal detail" in str(exc_info.value)

    def test_stderr_is_captured(self) -> None:
        result = CommandRunner().run(
            py_cmd("import sys; print('oops', file=sys.stderr)"),
            check=False,
            stream=False,
        )
        assert "oops" in result.output


class TestStreaming:
    def test_streams_and_captures(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = CommandRunner().run(py_cmd("print('live')"), stream=True)
        assert "live" in result.output
        assert "live" in capsys.readouterr().out

    def test_streaming_failure_raises(self) -> None:
        with pytest.raises(CommandExecutionError):
            CommandRunner().run(py_cmd("import sys; sys.exit(7)"), stream=True)


class TestCommandResult:
    def test_is_frozen(self) -> None:
        result = CommandResult(args=("a",), returncode=0, output="")
        with pytest.raises(FrozenInstanceError):
            result.returncode = 1  # type: ignore[misc]
