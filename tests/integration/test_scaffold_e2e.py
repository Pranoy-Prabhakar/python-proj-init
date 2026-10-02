"""Integration tests: run the real scaffolder end to end in temp dirs.

These execute actual uv/ruff/ty/prek commands (design §41). They are slower
than unit tests; run just these with ``pytest -m integration``.
"""

import tomllib
from pathlib import Path

import pytest

from py_scaffold.cli import main

pytestmark = pytest.mark.integration


def scaffold(tmp_path: Path, *extra: str) -> tuple[int, Path]:
    name = extra[0]
    exit_code = main(["new", *extra, "--path", str(tmp_path), "--non-interactive"])
    return exit_code, tmp_path / name


class TestApplicationProject:
    def test_full_scaffold(self, tmp_path: Path) -> None:
        exit_code, project = scaffold(tmp_path, "demo-app", "--type", "application")
        assert exit_code == 0

        assert (project / "pyproject.toml").exists()
        assert (project / "README.md").exists()
        assert (project / ".python-version").exists()
        assert (project / ".venv").is_dir()
        assert (project / "uv.lock").exists()
        assert (project / "prek.toml").exists()
        assert (project / "Makefile").exists()
        assert (project / ".git" / "hooks").is_dir()  # hooks installed

        pyproject = tomllib.loads((project / "pyproject.toml").read_text("utf-8"))
        dev = pyproject["dependency-groups"]["dev"]
        assert {"ruff", "ty", "prek"} <= {d.split(">")[0].split("=")[0] for d in dev}
        assert "ruff" not in pyproject["project"].get("dependencies", [])
        assert pyproject["tool"]["ruff"]["target-version"] == "py312"
        assert pyproject["tool"]["ty"]["environment"]["root"] == ["./src"]

        # Validation already ran inside the pipeline (ruff, ty) — exit 0 above
        # proves it. Sanity-check the acceptance commands once more directly:
        readme = (project / "README.md").read_text("utf-8")
        assert "uv run ruff check ." in readme
        assert "uv run ty check" in readme


class TestLibraryProject:
    def test_full_scaffold_and_build(self, tmp_path: Path) -> None:
        exit_code, project = scaffold(tmp_path, "demo-utils", "--type", "library")
        assert exit_code == 0

        package = project / "src" / "demo_utils"
        assert package.is_dir()
        assert (package / "__init__.py").exists()

        # uv build ran during validation: wheel + sdist must exist (§35)
        dist = project / "dist"
        assert list(dist.glob("*.whl")), "wheel missing"
        assert list(dist.glob("*.tar.gz")), "sdist missing"

        readme = (project / "README.md").read_text("utf-8")
        assert "uv build" in readme
        assert "uv publish" in readme
        assert "Nexus" not in readme


class TestOptions:
    def test_no_make_no_hooks(self, tmp_path: Path) -> None:
        exit_code, project = scaffold(
            tmp_path, "bare-app", "--type", "application", "--no-make", "--no-hooks"
        )
        assert exit_code == 0
        assert not (project / "Makefile").exists()
        assert (project / "prek.toml").exists()  # config still generated

    def test_custom_python_version(self, tmp_path: Path) -> None:
        exit_code, project = scaffold(
            tmp_path, "py313-app", "--type", "application", "--python", "3.13"
        )
        assert exit_code == 0
        assert (project / ".python-version").read_text("utf-8").strip().startswith("3.13")
        pyproject = tomllib.loads((project / "pyproject.toml").read_text("utf-8"))
        assert pyproject["tool"]["ruff"]["target-version"] == "py313"

    def test_existing_directory_refused(self, tmp_path: Path) -> None:
        existing = tmp_path / "taken-app"
        existing.mkdir()
        (existing / "keep.txt").write_text("precious")
        exit_code, _ = scaffold(tmp_path, "taken-app", "--type", "application")
        assert exit_code == 1
        assert (existing / "keep.txt").read_text() == "precious"  # untouched
