from __future__ import annotations

from pathlib import Path

import pytest

from yamlsan.schema import load_schema
from yamlsan.types import FieldType, Severity

FIXTURES = Path(__file__).parent / "fixtures"


class TestLoadSchema:
    def test_valid_yaml_schema(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        assert len(schema.fields) == 5

        title_field = next(f for f in schema.fields if f.name == "title")
        assert title_field.field_type == FieldType.STRING
        assert title_field.required is True

    def test_field_types(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")

        created_field = next(f for f in schema.fields if f.name == "created")
        assert created_field.field_type == FieldType.DATE
        assert created_field.pattern is not None

        tags_field = next(f for f in schema.fields if f.name == "tags")
        assert tags_field.field_type == FieldType.LIST
        assert tags_field.min_length == 1

    def test_allowed_values(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        status_field = next(f for f in schema.fields if f.name == "status")
        assert status_field.allowed == ("draft", "published", "archived")

    def test_defaults(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        priority_field = next(f for f in schema.fields if f.name == "priority")
        assert priority_field.default == 3
        assert priority_field.min_value == 1
        assert priority_field.max_value == 5

    def test_warning_severity(self):
        schema = load_schema(FIXTURES / "warning_schema.yaml")
        author_field = next(f for f in schema.fields if f.name == "author")
        assert author_field.severity == Severity.WARNING

    def test_json_schema(self, tmp_path):
        import json
        schema_data = {
            "fields": {
                "name": {"type": "string", "required": True},
            }
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema_data))
        schema = load_schema(schema_file)
        assert len(schema.fields) == 1
        assert schema.fields[0].name == "name"

    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_schema(Path("/nonexistent/schema.yaml"))

    def test_invalid_schema_structure(self, tmp_path):
        schema_file = tmp_path / "bad.yaml"
        schema_file.write_text("- item1\n- item2\n")
        with pytest.raises(ValueError, match="mapping"):
            load_schema(schema_file)
