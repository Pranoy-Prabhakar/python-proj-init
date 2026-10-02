"""Application project profile."""

from py_scaffold.config import ProjectConfig, ProjectType


class ApplicationProfile:
    """A runnable Python application (``uv init --app``)."""

    project_type = ProjectType.APPLICATION

    def init_command(self, config: ProjectConfig) -> list[str]:
        return [
            "uv",
            "init",
            "--app",
            "--python",
            config.python_version,
            config.name,
        ]

    def readme_template(self) -> str:
        return "README.application.md"
