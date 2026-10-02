"""Project profiles: application and library (design §26).

A profile decides *how* a project type is initialized (``uv init`` flavor)
and which README template it gets. Everything else in the pipeline is shared.
"""

from typing import Protocol

from py_scaffold.config import ProjectConfig, ProjectType


class ProjectProfile(Protocol):
    """Behavior that differs between project types."""

    project_type: ProjectType

    def init_command(self, config: ProjectConfig) -> list[str]:
        """The ``uv init`` argument list for this profile."""
        ...

    def readme_template(self) -> str:
        """Name of the README template packaged under ``templates/``."""
        ...


def get_profile(project_type: ProjectType) -> ProjectProfile:
    """Return the profile for ``project_type``."""
    from py_scaffold.profiles.application import ApplicationProfile
    from py_scaffold.profiles.library import LibraryProfile

    profiles: dict[ProjectType, ProjectProfile] = {
        ProjectType.APPLICATION: ApplicationProfile(),
        ProjectType.LIBRARY: LibraryProfile(),
    }
    return profiles[project_type]
