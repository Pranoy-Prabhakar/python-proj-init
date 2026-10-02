# $project_name

TODO: describe what this library does.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python $python_version (managed by uv — no manual install needed)
- Make (optional — every Makefile target is a plain uv command)

## Setup

```bash
uv sync
uv run prek install   # optional: Git hooks
```

## Installation

Once published:

```bash
uv add $project_name
```

For local development in another project:

```bash
uv add --editable /path/to/$project_name
```

## Development

```bash
uv run ruff check .          # lint
uv run ruff format .         # format
uv run ty check              # type check
uv run prek run --all-files  # all pre-commit hooks
```

Or with Make: `make lint`, `make format`, `make typecheck`, `make hooks`.

## Build

```bash
uv build
```

Artifacts (wheel + source distribution) are written to `dist/`.

## Publishing to PyPI

```bash
uv publish
```

Publishing is never automatic. Authentication must be configured separately
first — see the [uv publishing docs](https://docs.astral.sh/uv/guides/package/)
(PyPI token via `UV_PUBLISH_TOKEN` or trusted publishing). The scaffolder
never asks for or stores credentials.

## Pre-commit hooks

Hooks run Ruff (lint + format) and ty on every commit via
[prek](https://prek.j178.dev/). Configuration lives in `prek.toml`.
