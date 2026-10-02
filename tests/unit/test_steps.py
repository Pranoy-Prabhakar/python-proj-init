"""Unit tests for the individual generation steps."""

import tomllib
from collections.abc import Sequence
from pathlib import Path

import pytest

from py_scaffold.config import ProjectConfig, ProjectType
from py_scaffold.environment import EnvironmentStatus
from py_scaffold.errors import (
    DependencyInstallationError,
    HookInstallationError,
    PythonInstallationError,
    TargetDirectoryExistsError,
)
from py_scaffold.profiles import get_profile
from py_scaffold.runner import CommandResult, CommandRunner
from py_scaffold.steps.dependencies import install_dev_dependencies
from py_scaffold.steps.hooks import install_git_hooks, write_prek_config
from py_scaffold.steps.makefile import generate_makefile
from py_scaffold.steps.project_init import check_target_directory, initialize_project
from py_scaffold.steps.python_setup import ensure_python
from py_scaffold.steps.quality import configure_ruff, configure_ty
from py_scaffold.steps.readme import generate_readme


class FakeRunner(CommandRunner):
    """Canned responses; ``fails_on`` holds full command lines that exit 1."""

    def __init__(self, fails_on: set[str] | None = None) -> None:
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
        returncode = 1 if " ".join(argv) in self.fails_on else 0
        if check and returncode != 0:
            from py_scaffold.errors import CommandExecutionError

            raise CommandExecutionError(argv, returncode, f"failed: {' '.join(argv)}")
        return CommandResult(args=tuple(argv), returncode=returncode, output="")


def make_config(tmp_path: Path, project_type: ProjectType = ProjectType.LIBRARY) -> ProjectConfig:
    return ProjectConfig(
        name="demo-utils",
        package_name="demo_utils",
        project_type=project_type,
        python_version="3.12",
        destination=tmp_path,
    )


def make_project_dir(config: ProjectConfig) -> Path:
    """Simulate what uv init creates: a project dir with a pyproject.toml."""
    path = config.project_path
    path.mkdir(parents=True)
    (path / "pyproject.toml").write_text('[project]\nname = "demo-utils"\n', "utf-8")
    return path


class TestEnsurePython:
    def test_found(self) -> None:
        runner = FakeRunner()
        ensure_python("3.12", runner)
        assert runner.calls == [["uv", "python", "find", "3.12"]]

    def test_installs_when_missing(self) -> None:
        runner = FakeRunner(fails_on={"uv python find 3.12"})
        ensure_python("3.12", runner)
        assert runner.calls == [
            ["uv", "python", "find", "3.12"],
            ["uv", "python", "install", "3.12"],
        ]

    def test_install_failure_raises(self) -> None:
        runner = FakeRunner(fails_on={"uv python find 3.12", "uv python install 3.12"})
        with pytest.raises(PythonInstallationError):
            ensure_python("3.12", runner)


class TestCheckTargetDirectory:
    def test_missing_directory_is_fine(self, tmp_path: Path) -> None:
        check_target_directory(make_config(tmp_path))

    def test_empty_directory_is_fine(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        config.project_path.mkdir()
        check_target_directory(config)

    def test_non_empty_directory_rejected(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        config.project_path.mkdir()
        (config.project_path / "existing.txt").write_text("precious")
        with pytest.raises(TargetDirectoryExistsError):
            check_target_directory(config)


class TestInitializeProject:
    def test_creates_missing_destination(self, tmp_path: Path) -> None:
        config = make_config(tmp_path / "not-yet-created")
        runner = FakeRunner()
        initialize_project(config, get_profile(config.project_type), runner)
        assert config.destination.is_dir()
        assert runner.calls[0][:2] == ["uv", "init"]


class TestInstallDevDependencies:
    def test_command(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        runner = FakeRunner()
        install_dev_dependencies(config, runner)
        assert runner.calls == [["uv", "add", "--dev", "ruff", "ty", "prek"]]

    def test_failure_raises(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        runner = FakeRunner(fails_on={"uv add --dev ruff ty prek"})
        with pytest.raises(DependencyInstallationError):
            install_dev_dependencies(config, runner)


class TestQualityConfig:
    def test_ruff_block_appended_and_valid(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        project = make_project_dir(config)
        configure_ruff(config)
        data = tomllib.loads((project / "pyproject.toml").read_text("utf-8"))
        ruff = data["tool"]["ruff"]
        assert ruff["line-length"] == 100
        assert ruff["target-version"] == "py312"
        assert "E" in ruff["lint"]["select"]
        assert data["project"]["name"] == "demo-utils"  # original preserved

    def test_target_version_follows_python(self, tmp_path: Path) -> None:
        config = ProjectConfig(
            name="d",
            package_name="d",
            project_type=ProjectType.APPLICATION,
            python_version="3.13",
            destination=tmp_path,
        )
        project = make_project_dir(config)
        configure_ruff(config)
        data = tomllib.loads((project / "pyproject.toml").read_text("utf-8"))
        assert data["tool"]["ruff"]["target-version"] == "py313"

    def test_ty_block_appended(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        project = make_project_dir(config)
        configure_ty(config)
        data = tomllib.loads((project / "pyproject.toml").read_text("utf-8"))
        env = data["tool"]["ty"]["environment"]
        assert env["root"] == ["./src"]
        assert env["python-version"] == "3.12"


class TestHooks:
    def test_prek_config_written(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        project = make_project_dir(config)
        write_prek_config(config)
        content = (project / "prek.toml").read_text("utf-8")
        data = tomllib.loads(content)
        hooks = data["repos"][0]["hooks"]
        ids = {hook["id"] for hook in hooks}
        assert ids == {"ruff-format", "ruff-check", "ty-check"}

    def env(self, git: bool) -> EnvironmentStatus:
        return EnvironmentStatus(
            os="macos",
            uv_available=True,
            uv_version="0.12.13",
            git_available=git,
            make_available=False,
        )

    def test_installs_hooks(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        make_project_dir(config)
        runner = FakeRunner()
        install_git_hooks(config, self.env(git=True), runner, out=lambda _: None)
        commands = [" ".join(call) for call in runner.calls]
        assert "git init" in commands  # fresh project, not yet a repo
        assert "uv run prek install" in commands

    def test_skips_git_init_for_existing_repo(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        project = make_project_dir(config)
        (project / ".git").mkdir()
        runner = FakeRunner()
        install_git_hooks(config, self.env(git=True), runner, out=lambda _: None)
        commands = [" ".join(call) for call in runner.calls]
        assert "git init" not in commands
        assert "uv run prek install" in commands

    def test_skips_without_git(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        config = make_config(tmp_path)
        make_project_dir(config)
        runner = FakeRunner()
        install_git_hooks(config, self.env(git=False), runner)
        assert runner.calls == []
        assert "skipping" in capsys.readouterr().out.lower()

    def test_install_failure_raises(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        make_project_dir(config)
        runner = FakeRunner(fails_on={"uv run prek install"})
        with pytest.raises(HookInstallationError):
            install_git_hooks(config, self.env(git=True), runner, out=lambda _: None)


class TestMakefile:
    def test_generated(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        project = make_project_dir(config)
        generate_makefile(config)
        content = (project / "Makefile").read_text("utf-8")
        assert "lint:" in content
        assert "uv run ty check" in content
        assert "rm -rf" not in content  # no Unix-only destructive clean (§21)


class TestReadme:
    def test_application_readme(self, tmp_path: Path) -> None:
        config = make_config(tmp_path, ProjectType.APPLICATION)
        project = make_project_dir(config)
        generate_readme(config, get_profile(ProjectType.APPLICATION))
        content = (project / "README.md").read_text("utf-8")
        assert content.startswith("# demo-utils")
        assert "uv run ty check" in content
        assert "$project_name" not in content  # all placeholders substituted

    def test_library_readme_has_publish_docs(self, tmp_path: Path) -> None:
        config = make_config(tmp_path)
        project = make_project_dir(config)
        generate_readme(config, get_profile(ProjectType.LIBRARY))
        content = (project / "README.md").read_text("utf-8")
        assert "uv build" in content
        assert "uv publish" in content
        assert "Nexus" not in content  # §35: no Nexus configuration
