"""Library project profile."""

from py_scaffold.config import ProjectConfig, ProjectType


class LibraryProfile:
    """A publishable Python library (``uv init --lib``, ``uv build``)."""

    project_type = ProjectType.LIBRARY

    def init_command(self, config: ProjectConfig) -> list[str]:
        return [
            "uv",
            "init",
            "--lib",
            "--python",
            config.python_version,
            config.name,
        ]

    def readme_template(self) -> str:
        return "README.library.md"
