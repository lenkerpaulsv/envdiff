"""Tests for envdiff.reconciler."""

import pytest
from envdiff.core import DiffStatus, DiffEntry, EnvDiffResult
from envdiff.reconciler import reconcile, reconciled_to_env_string


def _make_entry(key, status, source=None, target=None):
    return DiffEntry(key=key, status=status, source_value=source, target_value=target)


def _make_result(*entries):
    return EnvDiffResult(entries=list(entries))


class TestReconcile:
    def test_unchanged_keys_always_included(self):
        result = _make_result(_make_entry("HOST", DiffStatus.UNCHANGED, "localhost", "localhost"))
        out = reconcile(result)
        assert out == {"HOST": "localhost"}

    def test_added_key_uses_placeholder_by_default(self):
        result = _make_result(_make_entry("NEW_KEY", DiffStatus.ADDED, source="secret"))
        out = reconcile(result)
        assert out["NEW_KEY"] == "FILL_ME_IN"

    def test_added_key_copies_value_when_no_placeholder(self):
        result = _make_result(_make_entry("NEW_KEY", DiffStatus.ADDED, source="secret"))
        out = reconcile(result, placeholder=None)
        assert out["NEW_KEY"] == "secret"

    def test_added_key_excluded_when_flag_false(self):
        result = _make_result(_make_entry("NEW_KEY", DiffStatus.ADDED, source="secret"))
        out = reconcile(result, include_added=False)
        assert "NEW_KEY" not in out

    def test_removed_key_excluded_by_default(self):
        result = _make_result(_make_entry("OLD_KEY", DiffStatus.REMOVED, target="old"))
        out = reconcile(result)
        assert "OLD_KEY" not in out

    def test_removed_key_included_when_flag_true(self):
        result = _make_result(_make_entry("OLD_KEY", DiffStatus.REMOVED, target="old"))
        out = reconcile(result, include_removed=True)
        assert out["OLD_KEY"] == "old"

    def test_changed_key_uses_source_value(self):
        result = _make_result(
            _make_entry("DB_URL", DiffStatus.CHANGED, source="new_db", target="old_db")
        )
        out = reconcile(result)
        assert out["DB_URL"] == "new_db"

    def test_changed_key_excluded_when_flag_false(self):
        result = _make_result(
            _make_entry("DB_URL", DiffStatus.CHANGED, source="new_db", target="old_db")
        )
        out = reconcile(result, include_changed=False)
        assert "DB_URL" not in out


class TestReconciledToEnvString:
    def test_simple_key_value(self):
        result = reconciled_to_env_string({"KEY": "value"})
        assert result == "KEY=value\n"

    def test_value_with_spaces_is_quoted(self):
        result = reconciled_to_env_string({"MSG": "hello world"})
        assert result == 'MSG="hello world"\n'

    def test_none_value_produces_empty(self):
        result = reconciled_to_env_string({"EMPTY": None})
        assert result == "EMPTY=\n"

    def test_multiple_keys(self):
        mapping = {"A": "1", "B": "2"}
        lines = reconciled_to_env_string(mapping).strip().splitlines()
        assert len(lines) == 2

    def test_empty_mapping_returns_empty_string(self):
        assert reconciled_to_env_string({}) == ""
