from __future__ import annotations

import argparse
import sys
from pathlib import Path

from yamlsan import __version__
from yamlsan.fixer import fix_target
from yamlsan.reporter import print_results
from yamlsan.schema import load_schema
from yamlsan.validator import validate_target


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yamlsan",
        description="YAML Frontmatter Schema Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  yamlsan validate ./vault/ --schema schema.yaml\n"
            "  yamlsan validate --ci ./docs/ --schema schema.yaml\n"
            "  yamlsan fix ./vault/ --schema schema.yaml --dry-run\n"
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"yamlsan {__version__}"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # validate
    val = sub.add_parser("validate", help="Validate frontmatter against schema")
    val.add_argument(
        "target",
        type=Path,
        help="File or directory to validate",
    )
    val.add_argument(
        "--schema", "-s",
        type=Path,
        required=True,
        help="Path to schema file (YAML or JSON)",
    )
    val.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: minimal output, exit 1 on violations",
    )

    # fix
    fix = sub.add_parser("fix", help="Auto-fix missing fields with defaults")
    fix.add_argument(
        "target",
        type=Path,
        help="File or directory to fix",
    )
    fix.add_argument(
        "--schema", "-s",
        type=Path,
        required=True,
        help="Path to schema file (YAML or JSON)",
    )
    fix.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "validate":
        if not args.target.exists():
            print(f"Error: target not found: {args.target}", file=sys.stderr)
            return 2
        if not args.schema.exists():
            print(f"Error: schema not found: {args.schema}", file=sys.stderr)
            return 2

        schema = load_schema(args.schema)
        results = validate_target(args.target, schema)
        return print_results(results, ci_mode=args.ci)

    if args.command == "fix":
        if not args.target.exists():
            print(f"Error: target not found: {args.target}", file=sys.stderr)
            return 2
        if not args.schema.exists():
            print(f"Error: schema not found: {args.schema}", file=sys.stderr)
            return 2

        changes = fix_target(args.target, args.schema, dry_run=args.dry_run)
        if not changes:
            print("No changes needed.")
            return 0

        action = "would be" if args.dry_run else "applied"
        for file_path, file_changes in changes:
            print(f"{file_path}:")
            for change in file_changes:
                print(f"  {change} ({action})")

        return 0

    return 0


def cli_entry() -> None:
    """Entry point for console_scripts."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
