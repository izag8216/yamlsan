from __future__ import annotations

import re
from typing import Any

from yamlsan.parser import collect_markdown_files, extract_frontmatter_from_file
from pathlib import Path

from yamlsan.types import (
    FieldType,
    FieldRule,
    SchemaDefinition,
    ValidationResult,
    Violation,
)


def _check_type(value: Any, field_type: FieldType) -> bool:
    if field_type == FieldType.ANY:
        return True
    if field_type == FieldType.STRING:
        return isinstance(value, str)
    if field_type == FieldType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    if field_type == FieldType.FLOAT:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if field_type == FieldType.BOOLEAN:
        return isinstance(value, bool)
    if field_type == FieldType.LIST:
        return isinstance(value, list)
    if field_type == FieldType.DATE:
        return isinstance(value, str) and bool(
            re.match(r"^\d{4}-\d{2}-\d{2}", value)
        )
    if field_type == FieldType.ENUM:
        return True
    return True


def _check_pattern(value: Any, pattern: str) -> bool:
    if not isinstance(value, str):
        return True
    return bool(re.match(pattern, value))


def _check_allowed(value: Any, allowed: tuple[str, ...]) -> bool:
    return value in allowed


def _check_min_length(value: Any, min_length: int) -> bool:
    if isinstance(value, (str, list)):
        return len(value) >= min_length
    return True


def _check_max_length(value: Any, max_length: int) -> bool:
    if isinstance(value, (str, list)):
        return len(value) <= max_length
    return True


def _check_min_value(value: Any, min_value: int | float) -> bool:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value >= min_value
    return True


def _check_max_value(value: Any, max_value: int | float) -> bool:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value <= max_value
    return True


def _validate_field(
    field_name: str,
    value: Any,
    rule: FieldRule,
    is_present: bool,
) -> list[Violation]:
    violations: list[Violation] = []

    if not is_present:
        if rule.required:
            violations.append(
                Violation(
                    file_path="",
                    field_name=field_name,
                    rule=rule,
                    message=f"Required field '{field_name}' is missing",
                    actual_value=None,
                )
            )
        return violations

    if not _check_type(value, rule.field_type):
        violations.append(
            Violation(
                file_path="",
                field_name=field_name,
                rule=rule,
                message=(
                    f"Field '{field_name}' has wrong type: "
                    f"expected {rule.field_type.value}, "
                    f"got {type(value).__name__}"
                ),
                actual_value=value,
            )
        )
        return violations

    if rule.pattern and not _check_pattern(value, rule.pattern):
        violations.append(
            Violation(
                file_path="",
                field_name=field_name,
                rule=rule,
                message=(
                    f"Field '{field_name}' does not match pattern: "
                    f"{rule.pattern}"
                ),
                actual_value=value,
            )
        )

    if rule.allowed and not _check_allowed(value, rule.allowed):
        violations.append(
            Violation(
                file_path="",
                field_name=field_name,
                rule=rule,
                message=(
                    f"Field '{field_name}' has invalid value: "
                    f"{value!r}. Allowed: {list(rule.allowed)}"
                ),
                actual_value=value,
            )
        )

    if rule.min_length is not None and not _check_min_length(value, rule.min_length):
        violations.append(
            Violation(
                file_path="",
                field_name=field_name,
                rule=rule,
                message=(
                    f"Field '{field_name}' is too short: "
                    f"min {rule.min_length}, got {len(value)}"
                ),
                actual_value=value,
            )
        )

    if rule.max_length is not None and not _check_max_length(value, rule.max_length):
        violations.append(
            Violation(
                file_path="",
                field_name=field_name,
                rule=rule,
                message=(
                    f"Field '{field_name}' is too long: "
                    f"max {rule.max_length}, got {len(value)}"
                ),
                actual_value=value,
            )
        )

    if rule.min_value is not None and not _check_min_value(value, rule.min_value):
        violations.append(
            Violation(
                file_path="",
                field_name=field_name,
                rule=rule,
                message=(
                    f"Field '{field_name}' is too small: "
                    f"min {rule.min_value}, got {value}"
                ),
                actual_value=value,
            )
        )

    if rule.max_value is not None and not _check_max_value(value, rule.max_value):
        violations.append(
            Violation(
                file_path="",
                field_name=field_name,
                rule=rule,
                message=(
                    f"Field '{field_name}' is too large: "
                    f"max {rule.max_value}, got {value}"
                ),
                actual_value=value,
            )
        )

    return violations


def validate_frontmatter(
    frontmatter: dict[str, Any],
    schema: SchemaDefinition,
    file_path: str = "",
) -> ValidationResult:
    """Validate a single frontmatter dict against a schema."""
    violations: list[Violation] = []

    for rule in schema.fields:
        value = frontmatter.get(rule.name)
        is_present = rule.name in frontmatter
        field_violations = _validate_field(
            rule.name, value, rule, is_present
        )
        for v in field_violations:
            violations.append(
                Violation(
                    file_path=file_path,
                    field_name=v.field_name,
                    rule=v.rule,
                    message=v.message,
                    actual_value=v.actual_value,
                )
            )

    return ValidationResult(file_path=file_path, violations=violations)


def validate_target(
    target: Path,
    schema: SchemaDefinition,
) -> list[ValidationResult]:
    """Validate all markdown files under target path against schema."""
    files = collect_markdown_files(target)
    results: list[ValidationResult] = []

    for fp in files:
        frontmatter = extract_frontmatter_from_file(fp)
        if frontmatter is None:
            results.append(
                ValidationResult(
                    file_path=str(fp),
                    violations=[],
                )
            )
            continue
        result = validate_frontmatter(frontmatter, schema, str(fp))
        results.append(result)

    return results
