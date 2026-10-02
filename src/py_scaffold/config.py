"""Configuration model for project generation."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ProjectType(StrEnum):
    """Supported project profiles."""

    APPLICATION = "application"
    LIBRARY = "library"


@dataclass(frozen=True)
class ProjectConfig:
    """Everything the generator needs to create one project.

    ``name`` is the distribution/directory name (e.g. ``payment-utils``);
    ``package_name`` is the derived Python import package (``payment_utils``).
    """

    name: str
    package_name: str
    project_type: ProjectType
    python_version: str
    destination: Path
    create_makefile: bool = True
    install_hooks: bool = True

    @property
    def project_path(self) -> Path:
        """Absolute path of the project directory that will be created."""
        return self.destination / self.name
