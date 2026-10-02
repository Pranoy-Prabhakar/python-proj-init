"""Unit tests for the generation pipeline orchestration."""

from collections.abc import Sequence
from pathlib import Path

import pytest

from py_scaffold.config import ProjectConfig, ProjectType
from py_scaffold.errors import (
    MissingUvError,
    ScaffoldError,
)
from py_scaffold.generator import create_project
from py_scaffold.runner import CommandResult, CommandRunner


class PipelineRunner(CommandRunner):
    """Simulates uv/git without touching the network or real uv.

    ``uv init`` creates the project directory and a minimal pyproject.toml,
    like the real thing; everything else just succeeds and is recorded.
    """

    def __init__(self, destination: Path, fails_on: set[str] | None = None) -> None:
        self.destination = destination
        self.fails_on = fails_on or set()
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
        line = " ".join(argv)

        if argv[:2] == ["uv", "init"]:
            name = argv[-1]
            project = self.destination / name
            project.mkdir(parents=True, exist_ok=True)
            (project / "pyproject.toml").write_text(f'[project]\nname = "{name}"\n', "utf-8")
        if argv[:2] == ["uv", "--version"][:2] and argv == ["uv", "--version"]:
            return CommandResult(args=tuple(argv), returncode=0, output="uv 0.12.13")

        returncode = 1 if line in self.fails_on else 0
        if check and returncode != 0:
            from py_scaffold.errors import CommandExecutionError

            raise CommandExecutionError(argv, returncode, f"failed: {line}")
        return CommandResult(args=tuple(argv), returncode=returncode, output="")


def make_config(tmp_path: Path, **overrides: object) -> ProjectConfig:
    defaults: dict[str, object] = {
        "name": "demo-utils",
        "package_name": "demo_utils",
        "project_type": ProjectType.LIBRARY,
        "python_version": "3.12",
        "destination": tmp_path,
        "install_hooks": False,
    }
    defaults.update(overrides)
    return ProjectConfig(**defaults)  # type: ignore[arg-type]


class TestHappyPath:
    def test_creates_all_files(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        create_project(config, runner=PipelineRunner(tmp_path), out=lambda _: None)

        project = config.project_path
        assert (project / "pyproject.toml").exists()
        assert (project / "prek.toml").exists()
        assert (project / "Makefile").exists()
        assert (project / "README.md").exists()

    def test_step_order(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        runner = PipelineRunner(tmp_path)
        create_project(config, runner=runner, out=lambda _: None)
        commands = [" ".join(call) for call in runner.calls]
        assert commands.index("uv python find 3.12") < commands.index(
            "uv init --lib --python 3.12 demo-utils"
        )
        assert commands.index("uv venv") < commands.index("uv sync")
        assert commands.index("uv add --dev ruff ty prek") < commands.index("uv build")

    def test_library_runs_build_validation(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        runner = PipelineRunner(tmp_path)
        create_project(config, runner=runner, out=lambda _: None)
        assert ["uv", "build"] in runner.calls

    def test_application_skips_build(self, tmp_path: Path) -> None:
        config = make_config(tmp_path, project_type=ProjectType.APPLICATION)
        runner = PipelineRunner(tmp_path)
        create_project(config, runner=runner, out=lambda _: None)
        assert ["uv", "build"] not in runner.calls

    def test_no_makefile_when_disabled(self, tmp_path: Path) -> None:
        config = make_config(tmp_path, create_makefile=False)
        create_project(config, runner=PipelineRunner(tmp_path), out=lambda _: None)
        assert not (config.project_path / "Makefile").exists()

    def test_hooks_installed_when_enabled(self, tmp_path: Path) -> None:
        config = make_config(tmp_path, install_hooks=True)
        runner = PipelineRunner(tmp_path)
        create_project(config, runner=runner, out=lambda _: None)
        commands = [" ".join(call) for call in runner.calls]
        assert "uv run prek install" in commands


class TestFailures:
    def test_existing_non_empty_directory(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        config.project_path.mkdir()
        (config.project_path / "precious.txt").write_text("do not touch")
        with pytest.raises(ScaffoldError, match="already exists"):
            create_project(config, runner=PipelineRunner(tmp_path), out=lambda _: None)
        assert (config.project_path / "precious.txt").read_text() == "do not touch"

    def test_step_failure_reports_partial_project(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        runner = PipelineRunner(tmp_path, fails_on={"uv add --dev ruff ty prek"})
        with pytest.raises(ScaffoldError, match="Partial project may remain"):
            create_project(config, runner=runner, out=lambda _: None)

    def test_missing_uv(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import shutil

        monkeypatch.setattr(shutil, "which", lambda tool: None)
        config = make_config(tmp_path)
        with pytest.raises(MissingUvError):
            create_project(config, runner=PipelineRunner(tmp_path), out=lambda _: None)
        assert not config.project_path.exists()  # nothing created (§39)


class TestProgressOutput:
    def test_success_symbols_printed(self, tmp_path: Path) -> None:
        lines: list[str] = []
        config = make_config(tmp_path)
        create_project(config, runner=PipelineRunner(tmp_path), out=lines.append)
        joined = "\n".join(lines)
        assert "Project initialized" in joined
        assert "Project validation passed" in joined
        assert "Project created successfully" in joined
