"""CLI sub-command: export  —  write a diff result to a file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.exporter import export_dotenv, export_json, export_yaml
from envdiff.parser import parse_env_file
from envdiff.core import EnvDiff


FORMAT_WRITERS = {
    "dotenv": export_dotenv,
    "json": export_json,
    "yaml": export_yaml,
}


def build_export_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *export* sub-command onto *subparsers*."""
    parser = subparsers.add_parser(
        "export",
        help="Export a diff result to dotenv / JSON / YAML format.",
    )
    parser.add_argument("staging", help="Path to the staging .env file.")
    parser.add_argument("production", help="Path to the production .env file.")
    parser.add_argument(
        "--format",
        choices=list(FORMAT_WRITERS),
        default="dotenv",
        dest="export_format",
        help="Output format (default: dotenv).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="Output file path.  Use '-' for stdout (default).",
    )
    parser.add_argument(
        "--include-removed",
        action="store_true",
        default=False,
        help="Include removed keys as comments (dotenv format only).",
    )
    parser.set_defaults(func=run_export)


def run_export(args: argparse.Namespace) -> int:
    """Execute the export sub-command.  Returns an exit code."""
    try:
        staging_env = parse_env_file(args.staging)
        production_env = parse_env_file(args.production)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = EnvDiff(staging_env, production_env).compare()
    writer = FORMAT_WRITERS[args.export_format]

    if args.export_format == "dotenv":
        output = writer(result, include_removed=args.include_removed)  # type: ignore[call-arg]
    else:
        output = writer(result)

    if args.output == "-":
        print(output)
    else:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Exported to {args.output}")

    return 0
