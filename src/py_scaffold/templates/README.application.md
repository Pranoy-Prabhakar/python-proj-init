# $project_name

TODO: describe what this application does.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python $python_version (managed by uv — no manual install needed)
- Make (optional — every Makefile target is a plain uv command)

## Setup

```bash
uv sync
uv run prek install   # optional: Git hooks
```

## Run

```bash
uv run python -m $package_name
```

## Development

```bash
uv run ruff check .          # lint
uv run ruff format .         # format
uv run ty check              # type check
uv run prek run --all-files  # all pre-commit hooks
```

Or with Make: `make lint`, `make format`, `make typecheck`, `make hooks`.

## Pre-commit hooks

Hooks run Ruff (lint + format) and ty on every commit via
[prek](https://prek.j178.dev/). Configuration lives in `prek.toml`.
