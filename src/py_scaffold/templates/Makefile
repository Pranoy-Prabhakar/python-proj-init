.PHONY: install sync format lint lint-fix typecheck check hooks setup build

install:
	uv sync

sync:
	uv sync

format:
	uv run ruff format .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

typecheck:
	uv run ty check

check: lint typecheck

hooks:
	uv run prek run --all-files

setup:
	uv sync
	uv run prek install

build:
	uv build
