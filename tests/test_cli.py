"""Tests for the envdiff CLI module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from envdiff.cli import run, build_parser
from envdiff.core import DiffStatus


STAGING_CONTENT = "FOO=bar\nBAZ=123\nONLY_STAGING=yes\n"
PRODUCTION_CONTENT = "FOO=bar\nBAZ=456\nONLY_PROD=yes\n"


@pytest.fixture
def env_files(tmp_path):
    staging = tmp_path / "staging.env"
    production = tmp_path / "production.env"
    staging.write_text(STAGING_CONTENT)
    production.write_text(PRODUCTION_CONTENT)
    return staging, production


class TestBuildParser:
    def test_defaults(self):
        parser = build_parser()
        args = parser.parse_args(["staging.env", "prod.env"])
        assert args.format == "text"
        assert args.show_unchanged is False

    def test_json_format_flag(self):
        parser = build_parser()
        args = parser.parse_args(["a.env", "b.env", "--format", "json"])
        assert args.format == "json"


class TestRunCLI:
    def test_returns_1_when_diff_exists(self, env_files):
        staging, production = env_files
        exit_code = run([str(staging), str(production)])
        assert exit_code == 1

    def test_returns_0_when_no_diff(self, tmp_path):
        content = "FOO=bar\n"
        a = tmp_path / "a.env"
        b = tmp_path / "b.env"
        a.write_text(content)
        b.write_text(content)
        assert run([str(a), str(b)]) == 0

    def test_missing_staging_returns_2(self, tmp_path):
        prod = tmp_path / "prod.env"
        prod.write_text("FOO=bar\n")
        exit_code = run([str(tmp_path / "nope.env"), str(prod)])
        assert exit_code == 2

    def test_missing_production_returns_2(self, tmp_path):
        staging = tmp_path / "staging.env"
        staging.write_text("FOO=bar\n")
        exit_code = run([str(staging), str(tmp_path / "nope.env")])
        assert exit_code == 2

    def test_json_output_is_valid(self, env_files, capsys):
        staging, production = env_files
        run([str(staging), str(production), "--format", "json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "entries" in data
        assert "summary" in data

    def test_summary_output(self, env_files, capsys):
        staging, production = env_files
        run([str(staging), str(production), "--format", "summary"])
        captured = capsys.readouterr()
        assert "modified" in captured.out or "added" in captured.out
