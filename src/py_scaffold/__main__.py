"""Allow running as ``python -m py_scaffold``."""

from py_scaffold.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
