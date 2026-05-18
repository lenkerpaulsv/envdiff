"""CLI entry point for the audit subcommand."""

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.core import diff
from envdiff.auditor import audit, AuditSeverity


def build_audit_parser(parent: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    parser = parent or argparse.ArgumentParser(
        prog="envdiff audit",
        description="Audit .env files for security and hygiene issues.",
    )
    parser.add_argument("staging", type=Path, help="Path to staging .env file")
    parser.add_argument("production", type=Path, help="Path to production .env file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="format",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        default=False,
        help="Exit with non-zero status if any warnings are found.",
    )
    return parser


def run_audit(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    staging = parse_env_file(args.staging)
    production = parse_env_file(args.production)
    diff_result = diff(staging, production)
    audit_result = audit(diff_result)

    if args.format == "json":
        payload = [
            {"key": i.key, "severity": i.severity.value, "message": i.message}
            for i in audit_result.issues
        ]
        out.write(json.dumps(payload, indent=2))
        out.write("\n")
    else:
        if not audit_result.issues:
            out.write("No audit issues found.\n")
        for issue in audit_result.issues:
            out.write(str(issue) + "\n")

    if audit_result.has_errors:
        return 2
    if args.fail_on_warning and audit_result.has_warnings:
        return 1
    return 0
