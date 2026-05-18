"""Tests for envdiff.cli_audit."""

import io
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from envdiff.cli_audit import build_audit_parser, run_audit
from envdiff.core import EnvDiffResult, DiffEntry, DiffStatus
from envdiff.auditor import AuditResult, AuditIssue, AuditSeverity


@pytest.fixture
def env_files(tmp_path):
    staging = tmp_path / "staging.env"
    production = tmp_path / "production.env"
    staging.write_text("APP_NAME=myapp\nAPI_TOKEN=changeme\n")
    production.write_text("APP_NAME=myapp\n")
    return staging, production


@pytest.fixture
def parser():
    return build_audit_parser()


class TestBuildAuditParser:
    def test_defaults(self, parser, env_files):
        staging, production = env_files
        args = parser.parse_args([str(staging), str(production)])
        assert args.format == "text"
        assert args.fail_on_warning is False

    def test_json_format_accepted(self, parser, env_files):
        staging, production = env_files
        args = parser.parse_args([str(staging), str(production), "--format", "json"])
        assert args.format == "json"

    def test_fail_on_warning_flag(self, parser, env_files):
        staging, production = env_files
        args = parser.parse_args([str(staging), str(production), "--fail-on-warning"])
        assert args.fail_on_warning is True


class TestRunAudit:
    def _run(self, staging, production, extra=None):
        p = build_audit_parser()
        argv = [str(staging), str(production)] + (extra or [])
        args = p.parse_args(argv)
        out, err = io.StringIO(), io.StringIO()
        code = run_audit(args, out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def test_clean_files_exit_zero(self, tmp_path):
        s = tmp_path / "s.env"
        p = tmp_path / "p.env"
        s.write_text("APP_NAME=myapp\n")
        p.write_text("APP_NAME=myapp\n")
        code, out, _ = self._run(s, p)
        assert code == 0
        assert "No audit issues found" in out

    def test_error_returns_exit_two(self, tmp_path):
        s = tmp_path / "s.env"
        p = tmp_path / "p.env"
        s.write_text("SECRET_KEY=changeme\n")
        p.write_text("SECRET_KEY=changeme\n")
        code, out, _ = self._run(s, p)
        assert code == 2

    def test_warning_with_fail_on_warning_returns_one(self, tmp_path):
        s = tmp_path / "s.env"
        p = tmp_path / "p.env"
        s.write_text("API_TOKEN=real_value\n")
        p.write_text("\n")
        code, out, _ = self._run(s, p, ["--fail-on-warning"])
        assert code in (1, 2)

    def test_json_output_is_valid(self, tmp_path):
        import json
        s = tmp_path / "s.env"
        p = tmp_path / "p.env"
        s.write_text("API_TOKEN=changeme\n")
        p.write_text("API_TOKEN=changeme\n")
        code, out, _ = self._run(s, p, ["--format", "json"])
        data = json.loads(out)
        assert isinstance(data, list)
        assert all("key" in item and "severity" in item for item in data)

    def test_text_output_contains_severity(self, tmp_path):
        s = tmp_path / "s.env"
        p = tmp_path / "p.env"
        s.write_text("SECRET_KEY=changeme\n")
        p.write_text("SECRET_KEY=changeme\n")
        _, out, _ = self._run(s, p)
        assert "ERROR" in out or "WARNING" in out
