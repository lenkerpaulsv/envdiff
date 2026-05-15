"""Command-line interface for envdiff."""

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.core import diff_envs
from envdiff.formatter import format_text, format_summary, format_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff and reconcile .env files across environments.",
    )
    parser.add_argument("staging", type=Path, help="Path to the staging .env file")
    parser.add_argument("production", type=Path, help="Path to the production .env file")
    parser.add_argument(
        "--format",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Include unchanged keys in text output",
    )
    return parser


def run(argv=None) -> int:
    """Entry point for the CLI. Returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        staging_vars = parse_env_file(args.staging)
    except FileNotFoundError:
        print(f"error: staging file not found: {args.staging}", file=sys.stderr)
        return 2

    try:
        production_vars = parse_env_file(args.production)
    except FileNotFoundError:
        print(f"error: production file not found: {args.production}", file=sys.stderr)
        return 2

    result = diff_envs(staging_vars, production_vars)

    if args.format == "text":
        output = format_text(result, show_unchanged=args.show_unchanged)
        if output:
            print(output)
    elif args.format == "summary":
        print(format_summary(result))
    elif args.format == "json":
        print(json.dumps(format_json(result), indent=2))

    has_diff = any(
        e.status.value != "unchanged" for e in result.entries
    )
    return 1 if has_diff else 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
