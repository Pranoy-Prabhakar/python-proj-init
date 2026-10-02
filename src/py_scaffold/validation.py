"""Project name validation and package-name derivation.

Names are validated before any file is created. A valid name is also a safe
relative path segment: no separators, no traversal, no spaces.
"""

import keyword
import re

from py_scaffold.errors import InvalidProjectNameError

# PEP 508-ish distribution name: alphanumerics separated by single - or _,
# starting and ending with an alphanumeric.
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9_-]*[A-Za-z0-9])?$")


def validate_project_name(name: str) -> str:
    """Return ``name`` if valid, otherwise raise :class:`InvalidProjectNameError`.

    Accepted: ``payment-service``, ``payment_service``, ``paymentutils``.
    Rejected: spaces, path separators, ``.``, ``..``, empty names.
    """
    if not name or not name.strip():
        raise InvalidProjectNameError("Project name must not be empty.")

    if name in {".", ".."}:
        raise InvalidProjectNameError(f"Invalid project name: {name!r}")

    if not _NAME_PATTERN.match(name):
        raise InvalidProjectNameError(
            f"Invalid project name: {name!r}. "
            "Use only letters, digits, hyphens and underscores; "
            "it must start and end with a letter or digit."
        )

    return name


def derive_distribution_name(name: str) -> str:
    """Normalize a project name into a distribution name (lowercase, hyphens)."""
    return re.sub(r"[-_]+", "-", name.strip().lower())


def derive_package_name(name: str) -> str:
    """Derive the Python import package name from a project name.

    ``payment-utils`` -> ``payment_utils``. The result must be a valid,
    non-keyword Python identifier.
    """
    package = re.sub(r"[-\s]+", "_", name.strip().lower())
    package = re.sub(r"_+", "_", package)

    if not package.isidentifier():
        raise InvalidProjectNameError(f"Cannot derive a valid Python package name from {name!r}.")
    if keyword.iskeyword(package):
        raise InvalidProjectNameError(
            f"Derived package name {package!r} is a Python keyword; "
            "choose a different project name."
        )
    return package
