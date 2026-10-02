# python-proj-init

Cross-platform Python project scaffolder powered by [uv](https://docs.astral.sh/uv/).

Creates standardized Python **application** and **library** projects with:

- managed Python version via `uv`
- virtual environment and dependency sync
- Ruff (lint + format) and ty (type checking), pre-configured
- prek pre-commit hooks
- optional Makefile
- PyPI-ready library builds (`uv build`)

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed
- Git (recommended, required for pre-commit hooks)

## Install

Install the command-line tool with `uv`:

```bash
uv tool install python-proj-init
```

Alternatively, use `pipx install python-proj-init`.

## Usage

```bash
# Interactive
uv run python-proj-init new

# Non-interactive
uv run python-proj-init new payment-utils --type library --python 3.12
```

Options: `--type application|library`, `--python VERSION`, `--path DIR`,
`--no-make`, `--no-hooks`, `--non-interactive`.

Bootstrap wrappers (uv check + handoff only, no generation logic):

```bash
scripts/setup.sh new my-app        # macOS/Linux
scripts\setup.ps1 new my-app       # Windows
```

## Development

```bash
uv sync
uv run pytest                      # all tests (integration tests run real uv)
uv run pytest -m "not integration" # fast unit tests only
uv run ruff check .                # lint
uv run ruff format .               # format
uv run ty check                    # type check
```

## Design

See [solution-design-python-project-scaffolder.md](solution-design-python-project-scaffolder.md)
— the source of truth for this implementation.
