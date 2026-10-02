"""Unit tests for the CLI: parsing, prompting, and config resolution."""

from collections.abc import Callable
from pathlib import Path

import pytest

from py_scaffold.cli import build_parser, collect_config, main
from py_scaffold.config import ProjectType
from py_scaffold.errors import InvalidProjectNameError, ScaffoldError


def scripted_input(answers: list[str]) -> Callable[[str], str]:
    """Return an ``input`` replacement that pops scripted answers."""
    remaining = list(answers)

    def _input(prompt: str) -> str:
        if not remaining:
            raise AssertionError(f"Unexpected prompt: {prompt!r}")
        return remaining.pop(0)

    return _input


def parse(*argv: str) -> object:
    return build_parser().parse_args(list(argv))


class TestParser:
    def test_new_with_name(self) -> None:
        args = parse("new", "demo-app")
        assert args.command == "new"  # type: ignore[attr-defined]
        assert args.name == "demo-app"  # type: ignore[attr-defined]

    def test_all_flags(self) -> None:
        args = parse(
            "new",
            "demo",
            "--type",
            "library",
            "--python",
            "3.13",
            "--path",
            "/tmp/x",
            "--no-make",
            "--no-hooks",
            "--non-interactive",
        )
        assert args.type == "library"  # type: ignore[attr-defined]
        assert args.python == "3.13"  # type: ignore[attr-defined]
        assert args.no_make is True  # type: ignore[attr-defined]
        assert args.no_hooks is True  # type: ignore[attr-defined]
        assert args.non_interactive is True  # type: ignore[attr-defined]

    def test_invalid_type_rejected(self) -> None:
        with pytest.raises(SystemExit):
            parse("new", "demo", "--type", "django")

    def test_command_required(self) -> None:
        with pytest.raises(SystemExit):
            parse()


class TestCollectConfigNonInteractive:
    def test_full_args(self, tmp_path: Path) -> None:
        args = parse(
            "new",
            "payment-utils",
            "--type",
            "library",
            "--python",
            "3.13",
            "--path",
            str(tmp_path),
            "--non-interactive",
        )
        config = collect_config(args)  # type: ignore[arg-type]
        assert config.name == "payment-utils"
        assert config.package_name == "payment_utils"
        assert config.project_type is ProjectType.LIBRARY
        assert config.python_version == "3.13"
        assert config.destination == tmp_path
        assert config.project_path == tmp_path / "payment-utils"

    def test_requires_name(self) -> None:
        args = parse("new", "--non-interactive")
        with pytest.raises(ScaffoldError, match="name is required"):
            collect_config(args)  # type: ignore[arg-type]

    def test_defaults(self, tmp_path: Path) -> None:
        args = parse("new", "demo", "--path", str(tmp_path), "--non-interactive")
        config = collect_config(args)  # type: ignore[arg-type]
        assert config.project_type is ProjectType.APPLICATION
        assert config.python_version == "3.12"
        assert config.create_makefile is True
        assert config.install_hooks is True

    def test_invalid_name_raises(self) -> None:
        args = parse("new", "bad name", "--non-interactive")
        with pytest.raises(InvalidProjectNameError):
            collect_config(args)  # type: ignore[arg-type]


class TestCollectConfigInteractive:
    def test_prompts_for_everything(self, tmp_path: Path) -> None:
        answers = scripted_input(["payment-utils", "2", "3.13"])
        args = parse("new", "--path", str(tmp_path))
        config = collect_config(args, input_fn=answers)  # type: ignore[arg-type]
        assert config.name == "payment-utils"
        assert config.project_type is ProjectType.LIBRARY
        assert config.python_version == "3.13"

    def test_prompt_defaults(self, tmp_path: Path) -> None:
        answers = scripted_input(["demo-app", "", ""])
        args = parse("new", "--path", str(tmp_path))
        config = collect_config(args, input_fn=answers)  # type: ignore[arg-type]
        assert config.project_type is ProjectType.APPLICATION
        assert config.python_version == "3.12"

    def test_type_by_name(self, tmp_path: Path) -> None:
        answers = scripted_input(["demo", "library", ""])
        args = parse("new", "--path", str(tmp_path))
        config = collect_config(args, input_fn=answers)  # type: ignore[arg-type]
        assert config.project_type is ProjectType.LIBRARY

    def test_invalid_type_selection(self, tmp_path: Path) -> None:
        answers = scripted_input(["demo", "9"])
        args = parse("new", "--path", str(tmp_path))
        with pytest.raises(ScaffoldError, match="Invalid project type"):
            collect_config(args, input_fn=answers)  # type: ignore[arg-type]

    def test_cli_args_skip_prompts(self, tmp_path: Path) -> None:
        answers = scripted_input([])  # any prompt would raise
        args = parse(
            "new",
            "demo",
            "--type",
            "application",
            "--python",
            "3.12",
            "--path",
            str(tmp_path),
        )
        collect_config(args, input_fn=answers)  # type: ignore[arg-type]


class TestMain:
    def test_non_interactive_success(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        created: list[object] = []
        monkeypatch.setattr("py_scaffold.cli.create_project", created.append)
        exit_code = main(["new", "demo", "--path", str(tmp_path), "--non-interactive"])
        assert exit_code == 0
        assert len(created) == 1
        assert created[0].name == "demo"  # type: ignore[attr-defined]

    def test_generator_failure_exit_code(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def boom(_config: object) -> None:
            raise ScaffoldError("boom")

        monkeypatch.setattr("py_scaffold.cli.create_project", boom)
        exit_code = main(["new", "demo", "--path", str(tmp_path), "--non-interactive"])
        assert exit_code == 1
        assert "boom" in capsys.readouterr().out

    def test_scaffold_error_exit_code(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main(["new", "bad name", "--non-interactive"])
        assert exit_code == 1
        assert "Invalid project name" in capsys.readouterr().out
