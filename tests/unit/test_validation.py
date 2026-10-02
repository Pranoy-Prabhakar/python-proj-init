"""Unit tests for project name validation and package-name derivation."""

import pytest

from py_scaffold.errors import InvalidProjectNameError
from py_scaffold.validation import (
    derive_distribution_name,
    derive_package_name,
    validate_project_name,
)


class TestValidateProjectName:
    @pytest.mark.parametrize(
        "name",
        [
            "payment-service",
            "payment_service",
            "paymentutils",
            "company-data-utils",
            "PaymentUtils",
            "a",
            "x1",
        ],
    )
    def test_accepts_valid_names(self, name: str) -> None:
        assert validate_project_name(name) == name

    @pytest.mark.parametrize(
        "name",
        [
            "",
            "   ",
            ".",
            "..",
            "payment service",
            "/payment",
            "../payment",
            "payment/service",
            "payment\\service",
            "-leading-hyphen",
            "trailing-hyphen-",
            "_leading_underscore",
            "trailing_underscore_",
        ],
    )
    def test_rejects_invalid_names(self, name: str) -> None:
        with pytest.raises(InvalidProjectNameError):
            validate_project_name(name)


class TestDeriveDistributionName:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("payment-utils", "payment-utils"),
            ("payment_utils", "payment-utils"),
            ("Payment_Utils", "payment-utils"),
            ("company--data__utils", "company-data-utils"),
        ],
    )
    def test_normalization(self, name: str, expected: str) -> None:
        assert derive_distribution_name(name) == expected


class TestDerivePackageName:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("payment-utils", "payment_utils"),
            ("payment_service", "payment_service"),
            ("paymentutils", "paymentutils"),
            ("Company-Data-Utils", "company_data_utils"),
        ],
    )
    def test_valid_package_names(self, name: str, expected: str) -> None:
        assert derive_package_name(name) == expected

    @pytest.mark.parametrize(
        "name",
        [
            "123utils",  # cannot start with a digit
            "class",  # Python keyword
        ],
    )
    def test_rejects_underivable_names(self, name: str) -> None:
        with pytest.raises(InvalidProjectNameError):
            derive_package_name(name)

    def test_result_is_identifier(self) -> None:
        assert derive_package_name("payment-utils").isidentifier()
