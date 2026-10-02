"""Unit tests for the ProjectConfig model."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from py_scaffold.config import ProjectConfig, ProjectType


def make_config(**overrides: object) -> ProjectConfig:
    defaults: dict[str, object] = {
        "name": "payment-utils",
        "package_name": "payment_utils",
        "project_type": ProjectType.LIBRARY,
        "python_version": "3.12",
        "destination": Path("/tmp/dest"),
    }
    defaults.update(overrides)
    return ProjectConfig(**defaults)  # type: ignore[arg-type]


class TestProjectType:
    def test_values(self) -> None:
        assert ProjectType.APPLICATION.value == "application"
        assert ProjectType.LIBRARY.value == "library"

    def test_str_enum(self) -> None:
        assert ProjectType.APPLICATION == "application"


class TestProjectConfig:
    def test_project_path(self) -> None:
        config = make_config()
        assert config.project_path == Path("/tmp/dest/payment-utils")

    def test_defaults(self) -> None:
        config = make_config()
        assert config.create_makefile is True
        assert config.install_hooks is True

    def test_frozen(self) -> None:
        config = make_config()
        with pytest.raises(FrozenInstanceError):
            config.name = "other"  # type: ignore[misc]
        assert config.name == "payment-utils"
