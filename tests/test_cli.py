from __future__ import annotations

from pathlib import Path

import pytest

from yamlsan.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class TestCLIValidate:
    def test_valid_file(self):
        exit_code = main([
            "validate",
            str(FIXTURES / "valid_doc.md"),
            "--schema", str(FIXTURES / "valid_schema.yaml"),
        ])
        assert exit_code == 0

    def test_invalid_file(self):
        exit_code = main([
            "validate",
            str(FIXTURES / "missing_required.md"),
            "--schema", str(FIXTURES / "valid_schema.yaml"),
        ])
        assert exit_code == 1

    def test_ci_mode(self):
        exit_code = main([
            "validate",
            "--ci",
            str(FIXTURES / "missing_required.md"),
            "--schema", str(FIXTURES / "valid_schema.yaml"),
        ])
        assert exit_code == 1

    def test_nonexistent_target(self):
        exit_code = main([
            "validate",
            "/nonexistent/path",
            "--schema", str(FIXTURES / "valid_schema.yaml"),
        ])
        assert exit_code == 2

    def test_nonexistent_schema(self):
        exit_code = main([
            "validate",
            str(FIXTURES / "valid_doc.md"),
            "--schema", "/nonexistent/schema.yaml",
        ])
        assert exit_code == 2

    def test_no_command(self):
        exit_code = main([])
        assert exit_code == 0


class TestCLIFix:
    def test_dry_run(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("---\ntitle: Test\n---\n\nBody.")
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n  status:\n    type: string\n"
            "    required: false\n    default: draft\n"
        )
        exit_code = main([
            "fix",
            str(doc),
            "--schema", str(schema),
            "--dry-run",
        ])
        assert exit_code == 0

    def test_apply(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("---\ntitle: Test\n---\n\nBody.")
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n  status:\n    type: string\n"
            "    required: false\n    default: draft\n"
        )
        exit_code = main([
            "fix",
            str(doc),
            "--schema", str(schema),
        ])
        assert exit_code == 0
        content = doc.read_text()
        assert "status" in content

    def test_no_changes_needed(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("---\ntitle: Test\nstatus: draft\n---\n\nBody.")
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n  status:\n    type: string\n"
            "    required: false\n    default: draft\n"
        )
        exit_code = main([
            "fix",
            str(doc),
            "--schema", str(schema),
        ])
        assert exit_code == 0
