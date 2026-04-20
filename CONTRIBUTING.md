# Contributing to yamlsan

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone and install with dev dependencies
git clone https://github.com/izag8216/yamlsan.git
cd yamlsan
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest                    # Run all tests
pytest --cov=yamlsan      # Run with coverage
pytest tests/test_parser.py  # Run specific module
```

## Coding Standards

- Python 3.10+
- Type hints on all public functions
- 80%+ test coverage
- Follow PEP 8 (max line length: 120)

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Write tests first (TDD encouraged)
4. Ensure all tests pass (`pytest`)
5. Commit with conventional commits (`feat:`, `fix:`, `docs:`, etc.)
6. Open a PR with a clear description

## Commit Convention

```
<type>: <description>

Types: feat, fix, refactor, docs, test, chore, perf
```

## Reporting Issues

Use GitHub Issues with the bug report or feature request templates.
