from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from yamlsan.types import FieldType, FieldRule, SchemaDefinition, Severity


_FIELD_TYPE_MAP = {
    "string": FieldType.STRING,
    "integer": FieldType.INTEGER,
    "int": FieldType.INTEGER,
    "float": FieldType.FLOAT,
    "number": FieldType.FLOAT,
    "boolean": FieldType.BOOLEAN,
    "bool": FieldType.BOOLEAN,
    "list": FieldType.LIST,
    "array": FieldType.LIST,
    "date": FieldType.DATE,
    "enum": FieldType.ENUM,
    "any": FieldType.ANY,
}


def _parse_field(name: str, definition: dict[str, Any]) -> FieldRule:
    raw_type = definition.get("type", "any").lower()
    field_type = _FIELD_TYPE_MAP.get(raw_type, FieldType.ANY)

    allowed_raw = definition.get("allowed")
    allowed = tuple(allowed_raw) if allowed_raw else None

    severity_raw = definition.get("severity", "error").lower()
    severity = Severity.WARNING if severity_raw == "warning" else Severity.ERROR

    return FieldRule(
        name=name,
        field_type=field_type,
        required=definition.get("required", True),
        allowed=allowed,
        pattern=definition.get("pattern"),
        default=definition.get("default"),
        min_length=definition.get("min_length"),
        max_length=definition.get("max_length"),
        min_value=definition.get("min_value"),
        max_value=definition.get("max_value"),
        severity=severity,
    )


def load_schema(schema_path: Path) -> SchemaDefinition:
    """Load a schema definition from YAML or JSON file."""
    text = schema_path.read_text(encoding="utf-8")

    if schema_path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(text)
    elif schema_path.suffix == ".json":
        data = json.loads(text)
    else:
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            data = json.loads(text)

    if not isinstance(data, dict):
        raise ValueError(f"Schema must be a mapping, got {type(data).__name__}")

    raw_fields = data.get("fields", {})
    if not isinstance(raw_fields, dict):
        raise ValueError("'fields' must be a mapping of field definitions")

    fields = tuple(
        _parse_field(name, defn) for name, defn in raw_fields.items()
    )

    return SchemaDefinition(
        fields=fields,
        name=data.get("name", "default"),
        description=data.get("description", ""),
        severity=Severity.ERROR,
    )
