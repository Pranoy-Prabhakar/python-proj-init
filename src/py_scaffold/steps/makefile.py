"""Makefile generation (§20–21).

Make is a convenience, never a requirement: the Makefile only wraps uv
commands, so everything works without it. No ``clean`` target in V1 — the
classic ``rm -rf`` version is Unix-only and Windows support is a hard goal.
"""

from importlib import resources

from py_scaffold.config import ProjectConfig


def generate_makefile(config: ProjectConfig) -> None:
    template = (resources.files("py_scaffold") / "templates" / "Makefile").read_text(
        encoding="utf-8"
    )
    (config.project_path / "Makefile").write_text(template, encoding="utf-8")
