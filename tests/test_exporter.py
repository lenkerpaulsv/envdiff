"""Tests for envdiff.exporter."""

from __future__ import annotations

import json

import pytest

from envdiff.core import DiffEntry, DiffStatus, EnvDiffResult
from envdiff.exporter import export_dotenv, export_json, export_yaml


def _entry(key: str, status: DiffStatus, left=None, right=None) -> DiffEntry:
    return DiffEntry(key=key, status=status, left_value=left, right_value=right)


def _make_result(*entries: DiffEntry) -> EnvDiffResult:
    return EnvDiffResult(entries=list(entries))


# ---------------------------------------------------------------------------
# export_dotenv
# ---------------------------------------------------------------------------

class TestExportDotenv:
    def test_unchanged_key_included(self):
        result = _make_result(_entry("PORT", DiffStatus.UNCHANGED, "8080", "8080"))
        assert "PORT=8080" in export_dotenv(result)

    def test_added_key_included(self):
        result = _make_result(_entry("NEW_KEY", DiffStatus.ADDED, None, "value"))
        assert "NEW_KEY=value" in export_dotenv(result)

    def test_changed_key_uses_right_value(self):
        result = _make_result(_entry("DB", DiffStatus.CHANGED, "old", "new"))
        assert "DB=new" in export_dotenv(result)

    def test_removed_key_excluded_by_default(self):
        result = _make_result(_entry("OLD", DiffStatus.REMOVED, "gone", None))
        output = export_dotenv(result)
        assert "OLD" not in output

    def test_removed_key_commented_when_flag_set(self):
        result = _make_result(_entry("OLD", DiffStatus.REMOVED, "gone", None))
        output = export_dotenv(result, include_removed=True)
        assert "# REMOVED: OLD=gone" in output

    def test_multiple_entries_order_preserved(self):
        result = _make_result(
            _entry("A", DiffStatus.UNCHANGED, "1", "1"),
            _entry("B", DiffStatus.ADDED, None, "2"),
        )
        lines = export_dotenv(result).splitlines()
        assert lines[0] == "A=1"
        assert lines[1] == "B=2"


# ---------------------------------------------------------------------------
# export_json
# ---------------------------------------------------------------------------

class TestExportJson:
    def test_returns_valid_json(self):
        result = _make_result(_entry("X", DiffStatus.UNCHANGED, "v", "v"))
        parsed = json.loads(export_json(result))
        assert "summary" in parsed
        assert "entries" in parsed

    def test_summary_counts(self):
        result = _make_result(
            _entry("A", DiffStatus.ADDED, None, "1"),
            _entry("B", DiffStatus.REMOVED, "2", None),
            _entry("C", DiffStatus.CHANGED, "3", "4"),
            _entry("D", DiffStatus.UNCHANGED, "5", "5"),
        )
        summary = json.loads(export_json(result))["summary"]
        assert summary["added"] == 1
        assert summary["removed"] == 1
        assert summary["changed"] == 1
        assert summary["unchanged"] == 1

    def test_entry_fields_present(self):
        result = _make_result(_entry("KEY", DiffStatus.CHANGED, "old", "new"))
        entry = json.loads(export_json(result))["entries"][0]
        assert entry["key"] == "KEY"
        assert entry["left_value"] == "old"
        assert entry["right_value"] == "new"


# ---------------------------------------------------------------------------
# export_yaml
# ---------------------------------------------------------------------------

class TestExportYaml:
    def test_contains_summary_block(self):
        result = _make_result(_entry("Z", DiffStatus.UNCHANGED, "z", "z"))
        output = export_yaml(result)
        assert "summary:" in output

    def test_contains_entries_block(self):
        result = _make_result(_entry("Z", DiffStatus.UNCHANGED, "z", "z"))
        output = export_yaml(result)
        assert "entries:" in output

    def test_key_in_output(self):
        result = _make_result(_entry("MY_VAR", DiffStatus.ADDED, None, "hello"))
        assert "MY_VAR" in export_yaml(result)
