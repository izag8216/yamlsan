[English](./README.md) | [Japanese](./README.ja.md)

<div align="center">
  <img src="./docs/header.svg" alt="yamlsan -- YAML Frontmatter Schema Validator" width="800"/>
</div>

<br/>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)
[![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](./tests)

</div>

**yamlsan** validates YAML frontmatter in your markdown files against a user-defined schema. Keep your Obsidian vault, blog, or documentation consistent -- no drifting fields, no missing metadata.

## Features

- **Schema-driven validation** -- Define required fields, types, allowed values, and regex patterns in YAML or JSON
- **Auto-fix** -- Apply default values for missing fields (`--dry-run` to preview)
- **CI-friendly** -- `--ci` flag for minimal output with proper exit codes
- **Recursive scanning** -- Point at a directory, validate all `.md` files
- **Rich output** -- Color-coded table with error/warning breakdown
- **Zero external APIs** -- Fully offline, no accounts, no cloud

## Installation

```bash
pip install yamlsan
```

Or from source:

```bash
git clone https://github.com/izag8216/yamlsan.git
cd yamlsan
pip install -e .
```

## Quick Start

### 1. Create a schema

```yaml
# schema.yaml
fields:
  title:
    type: string
    required: true
  created:
    type: date
    required: true
    pattern: "^\\d{4}-\\d{2}-\\d{2}$"
  status:
    type: string
    required: true
    allowed: ["draft", "published", "archived"]
  tags:
    type: list
    required: false
    min_length: 1
  priority:
    type: integer
    required: false
    min_value: 1
    max_value: 5
    default: 3
```

### 2. Validate your files

```bash
yamlsan validate ./vault/ --schema schema.yaml
```

### 3. Use in CI

```bash
yamlsan validate --ci ./docs/ --schema schema.yaml
# Exit code 0 = all valid, 1 = violations found, 2 = error
```

### 4. Auto-fix missing fields

```bash
# Preview changes
yamlsan fix ./vault/ --schema schema.yaml --dry-run

# Apply defaults
yamlsan fix ./vault/ --schema schema.yaml
```

## Schema Reference

Each field in the `fields` mapping supports:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `type` | string | `"any"` | `string`, `integer`, `float`, `boolean`, `list`, `date`, `enum`, `any` |
| `required` | boolean | `true` | Whether the field must be present |
| `allowed` | list | -- | Allowed values (enum) |
| `pattern` | string | -- | Regex pattern the value must match |
| `default` | any | -- | Default value for auto-fix |
| `min_length` | integer | -- | Minimum length for strings/lists |
| `max_length` | integer | -- | Maximum length for strings/lists |
| `min_value` | number | -- | Minimum value for numbers |
| `max_value` | number | -- | Maximum value for numbers |
| `severity` | string | `"error"` | `"error"` or `"warning"` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files valid (or help/version) |
| 1 | Validation violations found |
| 2 | Runtime error (file not found, bad schema) |

## Development

```bash
pip install -e ".[dev]"
pytest --cov=yamlsan
```

## License

MIT License -- see [LICENSE](./LICENSE) for details.
