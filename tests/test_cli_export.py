"""Tests for envdiff.cli_export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envdiff.cli_export import build_export_parser, run_export


@pytest.fixture()
def env_files(tmp_path: Path):
    staging = tmp_path / "staging.env"
    production = tmp_path / "production.env"
    staging.write_text("PORT=3000\nDEBUG=true\nOLD_KEY=gone\n")
    production.write_text("PORT=8080\nNEW_KEY=hello\n")
    return staging, production


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    build_export_parser(subs)
    return root


class TestBuildExportParser:
    def test_default_format_is_dotenv(self, parser):
        args = parser.parse_args(["export", "a.env", "b.env"])
        assert args.export_format == "dotenv"

    def test_json_format_accepted(self, parser):
        args = parser.parse_args(["export", "a.env", "b.env", "--format", "json"])
        assert args.export_format == "json"

    def test_yaml_format_accepted(self, parser):
        args = parser.parse_args(["export", "a.env", "b.env", "--format", "yaml"])
        assert args.export_format == "yaml"

    def test_default_output_is_stdout(self, parser):
        args = parser.parse_args(["export", "a.env", "b.env"])
        assert args.output == "-"

    def test_include_removed_flag(self, parser):
        args = parser.parse_args(["export", "a.env", "b.env", "--include-removed"])
        assert args.include_removed is True


class TestRunExport:
    def test_returns_zero_on_success(self, env_files, capsys):
        staging, production = env_files
        ns = argparse.Namespace(
            staging=str(staging),
            production=str(production),
            export_format="dotenv",
            output="-",
            include_removed=False,
        )
        assert run_export(ns) == 0

    def test_stdout_contains_shared_key(self, env_files, capsys):
        staging, production = env_files
        ns = argparse.Namespace(
            staging=str(staging),
            production=str(production),
            export_format="dotenv",
            output="-",
            include_removed=False,
        )
        run_export(ns)
        out = capsys.readouterr().out
        assert "PORT=8080" in out

    def test_json_output_is_valid(self, env_files, capsys):
        staging, production = env_files
        ns = argparse.Namespace(
            staging=str(staging),
            production=str(production),
            export_format="json",
            output="-",
            include_removed=False,
        )
        run_export(ns)
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "summary" in parsed

    def test_writes_to_file(self, env_files, tmp_path):
        staging, production = env_files
        out_file = tmp_path / "out.env"
        ns = argparse.Namespace(
            staging=str(staging),
            production=str(production),
            export_format="dotenv",
            output=str(out_file),
            include_removed=False,
        )
        run_export(ns)
        assert out_file.exists()
        assert "PORT" in out_file.read_text()

    def test_missing_file_returns_one(self, tmp_path):
        ns = argparse.Namespace(
            staging=str(tmp_path / "missing.env"),
            production=str(tmp_path / "also_missing.env"),
            export_format="dotenv",
            output="-",
            include_removed=False,
        )
        assert run_export(ns) == 1
