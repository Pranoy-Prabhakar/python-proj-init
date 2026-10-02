"""README generation from packaged templates (§22, §38).

Templates use ``string.Template`` (``$placeholder``) so TOML/Markdown braces
never collide with substitution syntax.
"""

from importlib import resources
from string import Template

from py_scaffold.config import ProjectConfig
from py_scaffold.profiles.base import ProjectProfile


def generate_readme(config: ProjectConfig, profile: ProjectProfile) -> None:
    template_text = (
        resources.files("py_scaffold") / "templates" / profile.readme_template()
    ).read_text(encoding="utf-8")
    rendered = Template(template_text).substitute(
        project_name=config.name,
        package_name=config.package_name,
        python_version=config.python_version,
    )
    (config.project_path / "README.md").write_text(rendered, encoding="utf-8")
