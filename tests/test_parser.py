from __future__ import annotations

from pathlib import Path

import pytest

from yamlsan.parser import (
    collect_markdown_files,
    extract_frontmatter,
    extract_frontmatter_from_file,
    strip_frontmatter,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestExtractFrontmatter:
    def test_valid_frontmatter(self):
        content = '---\ntitle: "Hello"\ndate: "2026-04-20"\n---\n\nBody text.'
        result = extract_frontmatter(content)
        assert result == {"title": "Hello", "date": "2026-04-20"}

    def test_empty_frontmatter(self):
        content = "---\n---\nBody."
        result = extract_frontmatter(content)
        assert result is not None
        assert result == {} or result is None

    def test_no_frontmatter(self):
        content = "# Just a heading\n\nNo frontmatter."
        result = extract_frontmatter(content)
        assert result is None

    def test_invalid_yaml(self):
        content = "---\n: invalid: yaml: [:\n---\nBody."
        result = extract_frontmatter(content)
        assert result is None

    def test_frontmatter_not_at_start(self):
        content = "\nSome text\n---\ntitle: Test\n---\nBody."
        result = extract_frontmatter(content)
        assert result is None

    def test_non_dict_yaml(self):
        content = "---\n- item1\n- item2\n---\nBody."
        result = extract_frontmatter(content)
        assert result is None

    def test_list_value(self):
        content = "---\ntags:\n  - python\n  - cli\n---\nBody."
        result = extract_frontmatter(content)
        assert result == {"tags": ["python", "cli"]}

    def test_boolean_value(self):
        content = "---\npublished: true\n---\nBody."
        result = extract_frontmatter(content)
        assert result == {"published": True}

    def test_integer_value(self):
        content = "---\ncount: 42\n---\nBody."
        result = extract_frontmatter(content)
        assert result == {"count": 42}


class TestExtractFrontmatterFromFile:
    def test_valid_file(self):
        path = FIXTURES / "valid_doc.md"
        result = extract_frontmatter_from_file(path)
        assert result is not None
        assert result["title"] == "Test Document"
        assert result["status"] == "draft"

    def test_no_frontmatter_file(self):
        path = FIXTURES / "no_frontmatter.md"
        result = extract_frontmatter_from_file(path)
        assert result is None

    def test_nonexistent_file(self):
        result = extract_frontmatter_from_file(Path("/nonexistent/file.md"))
        assert result is None


class TestCollectMarkdownFiles:
    def test_directory(self):
        files = collect_markdown_files(FIXTURES)
        assert len(files) > 0
        assert all(f.suffix == ".md" for f in files)

    def test_single_file(self):
        path = FIXTURES / "valid_doc.md"
        files = collect_markdown_files(path)
        assert files == [path]

    def test_non_md_file(self):
        path = FIXTURES / "valid_schema.yaml"
        files = collect_markdown_files(path)
        assert files == []


class TestStripFrontmatter:
    def test_strip_basic(self):
        content = "---\ntitle: Test\n---\n\nBody text."
        result = strip_frontmatter(content)
        assert "title" not in result
        assert "Body text." in result

    def test_no_frontmatter(self):
        content = "# Heading\n\nBody."
        result = strip_frontmatter(content)
        assert result == "# Heading\n\nBody."
