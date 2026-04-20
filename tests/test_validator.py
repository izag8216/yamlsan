from __future__ import annotations

from pathlib import Path

import pytest

from yamlsan.schema import load_schema
from yamlsan.validator import validate_frontmatter, validate_target
from yamlsan.types import Severity

FIXTURES = Path(__file__).parent / "fixtures"


class TestValidateFrontmatter:
    def test_valid_document(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": "Test",
            "created": "2026-04-20",
            "status": "draft",
            "tags": ["test"],
            "priority": 2,
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is True
        assert len(result.violations) == 0

    def test_missing_required_field(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {"status": "draft"}
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is False
        assert any("title" in v.message for v in result.violations)
        assert any("created" in v.message for v in result.violations)

    def test_wrong_type_integer_as_string(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": 123,
            "created": "2026-04-20",
            "status": "draft",
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is False
        assert any("wrong type" in v.message for v in result.violations)

    def test_invalid_allowed_value(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": "Test",
            "created": "2026-04-20",
            "status": "unknown",
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is False
        assert any("invalid value" in v.message for v in result.violations)

    def test_pattern_mismatch(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": "Test",
            "created": "not-a-date",
            "status": "draft",
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is False

    def test_min_value_violation(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": "Test",
            "created": "2026-04-20",
            "status": "draft",
            "priority": 0,
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is False
        assert any("too small" in v.message for v in result.violations)

    def test_max_value_violation(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": "Test",
            "created": "2026-04-20",
            "status": "draft",
            "priority": 10,
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is False
        assert any("too large" in v.message for v in result.violations)

    def test_min_length_violation(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": "Test",
            "created": "2026-04-20",
            "status": "draft",
            "tags": [],
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is False
        assert any("too short" in v.message for v in result.violations)

    def test_optional_field_absent_ok(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        fm = {
            "title": "Test",
            "created": "2026-04-20",
            "status": "draft",
        }
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is True

    def test_warning_severity_still_valid(self):
        schema = load_schema(FIXTURES / "warning_schema.yaml")
        fm = {"title": "Test"}
        result = validate_frontmatter(fm, schema)
        assert result.is_valid is True


class TestValidateTarget:
    def test_valid_file(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        results = validate_target(FIXTURES / "valid_doc.md", schema)
        assert len(results) == 1
        assert results[0].is_valid is True

    def test_invalid_file(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        results = validate_target(FIXTURES / "missing_required.md", schema)
        assert len(results) == 1
        assert results[0].is_valid is False

    def test_directory_scan(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        results = validate_target(FIXTURES, schema)
        assert len(results) > 0

    def test_no_frontmatter_file(self):
        schema = load_schema(FIXTURES / "valid_schema.yaml")
        results = validate_target(FIXTURES / "no_frontmatter.md", schema)
        assert len(results) == 1
        assert results[0].is_valid is True
        assert len(results[0].violations) == 0
