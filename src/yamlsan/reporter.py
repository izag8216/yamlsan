from __future__ import annotations

import sys
from typing import TextIO

from rich.console import Console
from rich.table import Table
from rich.text import Text

from yamlsan.types import Severity, ValidationResult


def _style_severity(severity: Severity) -> str:
    if severity == Severity.ERROR:
        return "bold red"
    return "bold yellow"


def format_violation(result: ValidationResult, use_color: bool = True) -> str:
    """Format a single validation result for display."""
    if not result.violations:
        return ""

    lines: list[str] = []
    for v in result.violations:
        severity_str = v.rule.severity.value.upper()
        marker = "x" if v.rule.severity == Severity.ERROR else "!"
        lines.append(
            f"  [{marker}] {severity_str}: {v.message}"
            f" (in {result.file_path})"
        )
    return "\n".join(lines)


def print_results(
    results: list[ValidationResult],
    ci_mode: bool = False,
    output: TextIO | None = None,
) -> int:
    """Print validation results. Returns exit code (0=pass, 1=fail)."""
    console = Console(file=output or sys.stderr)
    total_errors = 0
    total_warnings = 0
    total_files = len(results)
    files_with_issues = 0

    for result in results:
        if not result.violations:
            continue
        files_with_issues += 1
        errors = [v for v in result.violations if v.rule.severity == Severity.ERROR]
        warnings = [v for v in result.violations if v.rule.severity == Severity.WARNING]
        total_errors += len(errors)
        total_warnings += len(warnings)

    if not ci_mode:
        table = Table(title="yamlsan validation results", show_lines=True)
        table.add_column("File", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Issues", justify="right")

        for result in results:
            if not result.violations:
                table.add_row(result.file_path, "[green]OK[/green]", "0")
            else:
                err_count = sum(
                    1 for v in result.violations
                    if v.rule.severity == Severity.ERROR
                )
                warn_count = sum(
                    1 for v in result.violations
                    if v.rule.severity == Severity.WARNING
                )
                parts: list[str] = []
                if err_count:
                    parts.append(f"[red]{err_count} error{'s' if err_count > 1 else ''}[/red]")
                if warn_count:
                    parts.append(f"[yellow]{warn_count} warning{'s' if warn_count > 1 else ''}[/yellow]")
                table.add_row(
                    result.file_path,
                    "[red]FAIL[/red]" if err_count else "[yellow]WARN[/yellow]",
                    ", ".join(parts),
                )

        console.print(table)

        for result in results:
            if result.violations:
                console.print(f"\n[bold]{result.file_path}[/bold]:")
                for v in result.violations:
                    style = _style_severity(v.rule.severity)
                    console.print(
                        f"  [{style}]{v.rule.severity.value.upper()}[/]: {v.message}"
                    )
                    if v.actual_value is not None:
                        console.print(
                            f"    actual: [dim]{v.actual_value!r}[/dim]"
                        )
    else:
        for result in results:
            for v in result.violations:
                severity_str = v.rule.severity.value.upper()
                console.print(
                    f"{severity_str}: {v.message} (in {result.file_path})"
                )

    console.print()
    summary_parts: list[str] = []
    if total_errors:
        summary_parts.append(f"{total_errors} error(s)")
    if total_warnings:
        summary_parts.append(f"{total_warnings} warning(s)")
    summary = ", ".join(summary_parts) if summary_parts else "All valid"

    console.print(
        f"Files: {total_files} scanned, {files_with_issues} with issues. {summary}."
    )

    return 1 if total_errors > 0 else 0
