"""Tests for envdiff.formatter module."""

import pytest
from envdiff.core import DiffStatus, DiffEntry, EnvDiffResult
from envdiff.formatter import format_text, format_summary, format_json


def _make_result(*entries):
    return EnvDiffResult(entries=list(entries))


def _entry(key, status, old=None, new=None):
    return DiffEntry(key=key, status=status, old_value=old, new_value=new)


class TestFormatText:
    def test_added_entry(self):
        result = _make_result(_entry("FOO", DiffStatus.ADDED, new="bar"))
        output = format_text(result)
        assert "+ FOO='bar'" in output

    def test_removed_entry(self):
        result = _make_result(_entry("FOO", DiffStatus.REMOVED, old="bar"))
        output = format_text(result)
        assert "- FOO='bar'" in output

    def test_modified_entry(self):
        result = _make_result(_entry("FOO", DiffStatus.MODIFIED, old="old", new="new"))
        output = format_text(result)
        assert "~ FOO: 'old' -> 'new'" in output

    def test_unchanged_hidden_by_default(self):
        result = _make_result(_entry("FOO", DiffStatus.UNCHANGED, new="val"))
        output = format_text(result)
        assert output == ""

    def test_unchanged_shown_when_requested(self):
        result = _make_result(_entry("FOO", DiffStatus.UNCHANGED, new="val"))
        output = format_text(result, show_unchanged=True)
        assert "FOO" in output

    def test_multiple_entries_order_preserved(self):
        result = _make_result(
            _entry("A", DiffStatus.ADDED, new="1"),
            _entry("B", DiffStatus.REMOVED, old="2"),
        )
        lines = format_text(result).splitlines()
        assert lines[0].startswith("+")
        assert lines[1].startswith("-")


class TestFormatSummary:
    def test_empty_result(self):
        result = _make_result()
        assert format_summary(result) == "no differences"

    def test_counts_all_statuses(self):
        result = _make_result(
            _entry("A", DiffStatus.ADDED, new="1"),
            _entry("B", DiffStatus.REMOVED, old="2"),
            _entry("C", DiffStatus.MODIFIED, old="x", new="y"),
            _entry("D", DiffStatus.UNCHANGED, new="z"),
        )
        summary = format_summary(result)
        assert "1 added" in summary
        assert "1 removed" in summary
        assert "1 modified" in summary
        assert "1 unchanged" in summary

    def test_only_added(self):
        result = _make_result(_entry("X", DiffStatus.ADDED, new="v"))
        assert format_summary(result) == "1 added"


class TestFormatJson:
    def test_returns_dict(self):
        result = _make_result(_entry("FOO", DiffStatus.ADDED, new="bar"))
        data = format_json(result)
        assert isinstance(data, dict)
        assert "entries" in data
        assert "summary" in data

    def test_entry_fields(self):
        result = _make_result(_entry("FOO", DiffStatus.MODIFIED, old="a", new="b"))
        entry = format_json(result)["entries"][0]
        assert entry["key"] == "FOO"
        assert entry["old_value"] == "a"
        assert entry["new_value"] == "b"
        assert entry["status"] == DiffStatus.MODIFIED.value
