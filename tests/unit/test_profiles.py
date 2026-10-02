"""Unit tests for project profiles."""

from pathlib import Path

from py_scaffold.config import ProjectConfig, ProjectType
from py_scaffold.profiles import get_profile
from py_scaffold.profiles.application import ApplicationProfile
from py_scaffold.profiles.library import LibraryProfile


def make_config(project_type: ProjectType = ProjectType.APPLICATION) -> ProjectConfig:
    return ProjectConfig(
        name="demo-utils",
        package_name="demo_utils",
        project_type=project_type,
        python_version="3.12",
        destination=Path("/tmp/dest"),
    )


class TestGetProfile:
    def test_application(self) -> None:
        assert isinstance(get_profile(ProjectType.APPLICATION), ApplicationProfile)

    def test_library(self) -> None:
        assert isinstance(get_profile(ProjectType.LIBRARY), LibraryProfile)


class TestInitCommands:
    def test_application_command(self) -> None:
        command = get_profile(ProjectType.APPLICATION).init_command(make_config())
        assert command[:2] == ["uv", "init"]
        assert "--app" in command
        assert command[command.index("--python") + 1] == "3.12"
        assert command[-1] == "demo-utils"

    def test_library_command(self) -> None:
        command = get_profile(ProjectType.LIBRARY).init_command(make_config(ProjectType.LIBRARY))
        assert "--lib" in command
        assert "--app" not in command

    def test_readme_templates(self) -> None:
        assert get_profile(ProjectType.APPLICATION).readme_template() == "README.application.md"
        assert get_profile(ProjectType.LIBRARY).readme_template() == "README.library.md"
