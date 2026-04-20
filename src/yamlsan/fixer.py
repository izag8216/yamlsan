from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from yamlsan.parser import extract_frontmatter, strip_frontmatter
from yamlsan.schema import load_schema
from yamlsan.types import SchemaDefinition, Violation


def _apply_defaults(
    frontmatter: dict[str, Any],
    schema: SchemaDefinition,
) -> dict[str, Any]:
    """Apply default values for missing fields that have defaults defined."""
    updated = dict(frontmatter)
    for rule in schema.fields:
        if rule.name not in updated and rule.default is not None:
            updated[rule.name] = rule.default
    return updated


def _fix_frontmatter(
    file_path: Path,
    schema: SchemaDefinition,
    dry_run: bool = False,
) -> list[str]:
    """Fix frontmatter by applying defaults. Returns list of changes made."""
    content = file_path.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)
    if frontmatter is None:
        return []

    fixed = _apply_defaults(frontmatter, schema)
    if fixed == frontmatter:
        return []

    changes: list[str] = []
    for rule in schema.fields:
        if rule.name not in frontmatter and rule.name in fixed:
            changes.append(
                f"  + {rule.name}: {fixed[rule.name]!r} (default applied)"
            )

    if dry_run:
        return changes

    body = strip_frontmatter(content)
    new_fm = yaml.dump(fixed, allow_unicode=True, default_flow_style=False)
    new_content = f"---\n{new_fm}---\n{body}"
    file_path.write_text(new_content, encoding="utf-8")

    return changes


def fix_target(
    target: Path,
    schema_path: Path,
    dry_run: bool = False,
) -> list[tuple[str, list[str]]]:
    """Fix all markdown files under target. Returns (file, changes) pairs."""
    schema = load_schema(schema_path)
    results: list[tuple[str, list[str]]] = []

    if target.is_file():
        if target.suffix == ".md":
            changes = _fix_frontmatter(target, schema, dry_run)
            if changes:
                results.append((str(target), changes))
        return results

    for fp in sorted(target.rglob("*.md")):
        changes = _fix_frontmatter(fp, schema, dry_run)
        if changes:
            results.append((str(fp), changes))

    return results
