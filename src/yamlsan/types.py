from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FieldType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DATE = "date"
    ENUM = "enum"
    ANY = "any"


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class FieldRule:
    name: str
    field_type: FieldType = FieldType.ANY
    required: bool = True
    allowed: tuple[str, ...] | None = None
    pattern: str | None = None
    default: Any = None
    min_length: int | None = None
    max_length: int | None = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    severity: Severity = Severity.ERROR


@dataclass(frozen=True)
class Violation:
    file_path: str
    field_name: str
    rule: FieldRule
    message: str
    actual_value: Any = None


@dataclass(frozen=True)
class SchemaDefinition:
    fields: tuple[FieldRule, ...]
    name: str = "default"
    description: str = ""
    severity: Severity = Severity.ERROR


@dataclass
class ValidationResult:
    file_path: str
    violations: list[Violation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(
            v.rule.severity == Severity.ERROR for v in self.violations
        )

    @property
    def has_warnings(self) -> bool:
        return any(
            v.rule.severity == Severity.WARNING for v in self.violations
        )
