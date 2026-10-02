"""Unit tests for EnvironmentChecker and require_uv."""

from collections.abc import Sequence
from pathlib import Path

import pytest

from py_scaffold.environment import EnvironmentChecker, require_uv
from py_scaffold.errors import MissingUvError
from py_scaffold.runner import CommandResult, CommandRunner


class FakeRunner(CommandRunner):
    """Returns canned command results keyed by the first argument."""

    def __init__(self, outputs: dict[str, str], returncode: int = 0) -> None:
        self.outputs = outputs
        self.returncode = returncode
        self.calls: list[list[str]] = []

    def run(
        self,
        command: Sequence[str],
        cwd: Path | None = None,
        check: bool = True,
        stream: bool = True,
    ) -> CommandResult:
        argv = [str(part) for part in command]
        self.calls.append(argv)
        output = self.outputs.get(argv[0], "")
        return CommandResult(args=tuple(argv), returncode=self.returncode, output=output)


def fake_which(available: set[str]):
    return lambda tool: f"/usr/bin/{tool}" if tool in available else None


class TestDetection:
    def test_all_tools_available(self) -> None:
        checker = EnvironmentChecker(
            runner=FakeRunner({"uv": "uv 0.12.13 (Homebrew)"}),
            which=fake_which({"uv", "git", "make"}),
        )
        status = checker.inspect()
        assert status.uv_available is True
        assert status.git_available is True
        assert status.make_available is True
        assert status.uv_version == "0.12.13"

    def test_missing_tools(self) -> None:
        checker = EnvironmentChecker(runner=FakeRunner({}), which=fake_which(set()))
        status = checker.inspect()
        assert status.uv_available is False
        assert status.git_available is False
        assert status.make_available is False
        assert status.uv_version is None

    def test_uv_version_not_queried_when_uv_missing(self) -> None:
        runner = FakeRunner({"uv": "uv 0.12.13"})
        checker = EnvironmentChecker(runner=runner, which=fake_which(set()))
        assert checker.uv_version() is None
        assert runner.calls == []

    def test_uv_version_unparseable(self) -> None:
        checker = EnvironmentChecker(
            runner=FakeRunner({"uv": "garbage"}),
            which=fake_which({"uv"}),
        )
        assert checker.uv_version() is None


class TestGetOs:
    @pytest.mark.parametrize(
        ("system", "expected"),
        [("Darwin", "macos"), ("Windows", "windows"), ("Linux", "linux")],
    )
    def test_normalization(
        self, system: str, expected: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("platform.system", lambda: system)
        assert EnvironmentChecker(which=fake_which(set())).get_os() == expected


class TestRequireUv:
    def test_passes_when_available(self) -> None:
        checker = EnvironmentChecker(runner=FakeRunner({}), which=fake_which({"uv"}))
        require_uv(checker.inspect())  # should not raise

    def test_raises_with_unix_guidance(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("platform.system", lambda: "Darwin")
        checker = EnvironmentChecker(which=fake_which(set()))
        with pytest.raises(MissingUvError) as exc_info:
            require_uv(checker.inspect())
        assert "astral.sh/uv/install.sh" in str(exc_info.value)

    def test_raises_with_windows_guidance(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("platform.system", lambda: "Windows")
        checker = EnvironmentChecker(which=fake_which(set()))
        with pytest.raises(MissingUvError) as exc_info:
            require_uv(checker.inspect())
        assert "install.ps1" in str(exc_info.value)
