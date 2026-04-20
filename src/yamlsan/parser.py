from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


FRONTMATTER_PATTERN = re.compile(
    r"\A---\s*\n(.*?)\n?---\s*\n?", re.DOTALL
)


def extract_frontmatter(content: str) -> dict[str, Any] | None:
    """Extract YAML frontmatter from markdown content."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return None
    try:
        parsed = yaml.safe_load(match.group(1))
        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            return None
        return parsed
    except yaml.YAMLError:
        return None


def extract_frontmatter_from_file(file_path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    return extract_frontmatter(content)


def collect_markdown_files(target: Path) -> list[Path]:
    """Recursively collect all .md files from target path."""
    if target.is_file():
        if target.suffix == ".md":
            return [target]
        return []
    return sorted(target.rglob("*.md"))


def strip_frontmatter(content: str) -> str:
    """Return content with frontmatter removed."""
    return FRONTMATTER_PATTERN.sub("", content).lstrip("\n")
