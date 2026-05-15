"""Tests for envdiff.validator."""

import pytest
from envdiff.validator import (
    ValidationIssue,
    ValidationResult,
    validate_keys,
    validate_no_empty_values,
    validate_env,
)


class TestValidationResult:
    def test_is_valid_when_empty(self):
        result = ValidationResult()
        assert result.is_valid is True

    def test_not_valid_after_add(self):
        result = ValidationResult()
        result.add("BAD KEY", "some message")
        assert result.is_valid is False

    def test_str_no_issues(self):
        result = ValidationResult()
        assert "No validation issues" in str(result)

    def test_str_with_issues(self):
        result = ValidationResult()
        result.add("BAD KEY", "not valid", line_number=3)
        output = str(result)
        assert "1 issue(s)" in output
        assert "line 3" in output


class TestValidateKeys:
    def test_valid_keys_pass(self):
        env = {"DATABASE_URL": "postgres://", "PORT": "5432", "_PRIVATE": "x"}
        result = validate_keys(env)
        # May still have lowercase warnings; check no POSIX errors
        posix_issues = [i for i in result.issues if "POSIX" in i.message]
        assert posix_issues == []

    def test_key_with_space_fails(self):
        env = {"BAD KEY": "value"}
        result = validate_keys(env)
        assert not result.is_valid
        assert any("POSIX" in i.message for i in result.issues)

    def test_key_starting_with_digit_fails(self):
        env = {"1INVALID": "value"}
        result = validate_keys(env)
        assert not result.is_valid

    def test_lowercase_key_warns(self):
        env = {"my_var": "value"}
        result = validate_keys(env)
        assert any("lowercase" in i.message for i in result.issues)

    def test_uppercase_key_no_case_warning(self):
        env = {"MY_VAR": "value"}
        result = validate_keys(env)
        case_issues = [i for i in result.issues if "lowercase" in i.message]
        assert case_issues == []


class TestValidateNoEmptyValues:
    def test_non_empty_values_pass(self):
        env = {"KEY": "value", "OTHER": "123"}
        result = validate_no_empty_values(env)
        assert result.is_valid

    def test_empty_value_flagged(self):
        env = {"EMPTY_KEY": ""}
        result = validate_no_empty_values(env)
        assert not result.is_valid
        assert result.issues[0].key == "EMPTY_KEY"


class TestValidateEnv:
    def test_combines_all_checks(self):
        env = {"bad key": "", "GOOD_KEY": "val"}
        result = validate_env(env)
        keys_in_issues = {i.key for i in result.issues}
        assert "bad key" in keys_in_issues

    def test_clean_env_passes(self):
        env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"}
        result = validate_env(env)
        assert result.is_valid
