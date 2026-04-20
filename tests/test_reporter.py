from __future__ import annotations

from io import StringIO
from pathlib import Path

from yamlsan.reporter import print_results
from yamlsan.types import (
    FieldRule,
    FieldType,
    SchemaDefinition,
    Severity,
    ValidationResult,
    Violation,
)


def _make_rule(
    name: str = "title",
    severity: Severity = Severity.ERROR,
) -> FieldRule:
    return FieldRule(
        name=name,
        field_type=FieldType.STRING,
        required=True,
        severity=severity,
    )


class TestPrintResults:
    def test_all_valid(self):
        results = [
            ValidationResult(file_path="a.md", violations=[]),
            ValidationResult(file_path="b.md", violations=[]),
        ]
        output = StringIO()
        exit_code = print_results(results, output=output)
        assert exit_code == 0

    def test_with_errors(self):
        rule = _make_rule()
        results = [
            ValidationResult(
                file_path="a.md",
                violations=[
                    Violation(
                        file_path="a.md",
                        field_name="title",
                        rule=rule,
                        message="Required field 'title' is missing",
                    )
                ],
            )
        ]
        output = StringIO()
        exit_code = print_results(results, output=output)
        assert exit_code == 1

    def test_warnings_only(self):
        rule = _make_rule(severity=Severity.WARNING)
        results = [
            ValidationResult(
                file_path="a.md",
                violations=[
                    Violation(
                        file_path="a.md",
                        field_name="title",
                        rule=rule,
                        message="Field 'title' has warning",
                    )
                ],
            )
        ]
        output = StringIO()
        exit_code = print_results(results, output=output)
        assert exit_code == 0

    def test_ci_mode(self):
        rule = _make_rule()
        results = [
            ValidationResult(
                file_path="a.md",
                violations=[
                    Violation(
                        file_path="a.md",
                        field_name="title",
                        rule=rule,
                        message="Required field 'title' is missing",
                    )
                ],
            )
        ]
        output = StringIO()
        exit_code = print_results(results, ci_mode=True, output=output)
        assert exit_code == 1
        text = output.getvalue()
        assert "ERROR" in text
        assert "a.md" in text
