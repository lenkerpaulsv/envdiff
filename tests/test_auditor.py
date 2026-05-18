"""Tests for envdiff.auditor."""

import pytest
from envdiff.auditor import audit, AuditSeverity, AuditIssue, AuditResult
from envdiff.core import EnvDiffResult, DiffEntry, DiffStatus


def _entry(key, status=DiffStatus.UNCHANGED, staging=None, production=None):
    return DiffEntry(
        key=key,
        status=status,
        staging_value=staging,
        production_value=production,
    )


def _make_result(*entries):
    return EnvDiffResult(entries=list(entries))


class TestAuditResult:
    def test_empty_has_no_errors(self):
        ar = AuditResult()
        assert not ar.has_errors
        assert not ar.has_warnings
        assert len(ar) == 0

    def test_add_issue_increments_len(self):
        ar = AuditResult()
        ar.add(AuditIssue(key="X", message="msg", severity=AuditSeverity.WARNING))
        assert len(ar) == 1

    def test_has_errors_detects_error_severity(self):
        ar = AuditResult()
        ar.add(AuditIssue(key="X", message="msg", severity=AuditSeverity.ERROR))
        assert ar.has_errors
        assert not ar.has_warnings

    def test_str_format(self):
        issue = AuditIssue(key="MY_KEY", message="bad value", severity=AuditSeverity.ERROR)
        assert str(issue) == "[ERROR] MY_KEY: bad value"


class TestAudit:
    def test_no_issues_for_clean_result(self):
        result = _make_result(_entry("APP_NAME", staging="myapp", production="myapp"))
        ar = audit(result)
        assert len(ar) == 0

    def test_sensitive_added_key_raises_warning(self):
        result = _make_result(
            _entry("API_TOKEN", status=DiffStatus.ADDED, staging="abc123")
        )
        ar = audit(result)
        severities = [i.severity for i in ar.issues]
        assert AuditSeverity.WARNING in severities

    def test_sensitive_removed_key_raises_warning(self):
        result = _make_result(
            _entry("DB_PASSWORD", status=DiffStatus.REMOVED, production="hunter2")
        )
        ar = audit(result)
        assert any(i.key == "DB_PASSWORD" for i in ar.issues)

    def test_placeholder_value_raises_error(self):
        result = _make_result(
            _entry("SECRET_KEY", status=DiffStatus.UNCHANGED, staging="changeme", production="changeme")
        )
        ar = audit(result)
        assert ar.has_errors
        error_msgs = [i.message for i in ar.issues if i.severity == AuditSeverity.ERROR]
        assert any("placeholder" in m for m in error_msgs)

    def test_lowercase_key_raises_warning(self):
        result = _make_result(
            _entry("appname", status=DiffStatus.UNCHANGED, staging="foo", production="foo")
        )
        ar = audit(result)
        assert any("uppercase" in i.message for i in ar.issues)

    def test_uppercase_key_no_case_warning(self):
        result = _make_result(
            _entry("APP_NAME", status=DiffStatus.UNCHANGED, staging="foo", production="foo")
        )
        ar = audit(result)
        assert not any("uppercase" in i.message for i in ar.issues)

    def test_multiple_issues_accumulated(self):
        result = _make_result(
            _entry("api_secret", status=DiffStatus.ADDED, staging="todo"),
        )
        ar = audit(result)
        assert len(ar) >= 2
