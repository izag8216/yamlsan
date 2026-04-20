from __future__ import annotations

from pathlib import Path

import pytest

from yamlsan.fixer import fix_target

FIXTURES = Path(__file__).parent / "fixtures"


class TestFixTarget:
    def test_dry_run_no_changes(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text(
            "---\ntitle: Test\nstatus: draft\npriority: 3\n---\n\nBody."
        )
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n    required: true\n"
            "  status:\n    type: string\n    required: false\n    default: draft\n"
        )
        changes = fix_target(doc, schema, dry_run=True)
        assert len(changes) == 0

    def test_dry_run_applies_defaults(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("---\ntitle: Test\n---\n\nBody.")
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n    required: true\n"
            "  status:\n    type: string\n    required: false\n    default: draft\n"
            "  priority:\n    type: integer\n    required: false\n    default: 3\n"
        )
        changes = fix_target(doc, schema, dry_run=True)
        assert len(changes) == 1
        file_path, file_changes = changes[0]
        assert len(file_changes) == 2

    def test_apply_fixes(self, tmp_path):
        doc = tmp_path / "doc.md"
        original = "---\ntitle: Test\n---\n\nBody."
        doc.write_text(original)
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n    required: true\n"
            "  status:\n    type: string\n    required: false\n    default: published\n"
        )
        fix_target(doc, schema, dry_run=False)
        content = doc.read_text()
        assert "status" in content
        assert "published" in content

    def test_no_frontmatter_file(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("# No frontmatter\n\nBody.")
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n    required: true\n"
        )
        changes = fix_target(doc, schema, dry_run=True)
        assert len(changes) == 0

    def test_directory_fix(self, tmp_path):
        for name in ["a.md", "b.md"]:
            (tmp_path / name).write_text("---\ntitle: Test\n---\n\nBody.")
        schema = tmp_path / "schema.yaml"
        schema.write_text(
            "fields:\n  title:\n    type: string\n    required: true\n"
            "  status:\n    type: string\n    required: false\n    default: draft\n"
        )
        changes = fix_target(tmp_path, schema, dry_run=True)
        assert len(changes) == 2
