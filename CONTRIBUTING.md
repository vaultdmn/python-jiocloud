# Contributing to python-jiocloud

Thank you for your interest in contributing to `python-jiocloud`!

## Development Setup

1. Fork and clone the repository.
2. Create a virtual environment and install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests, linter, and type checker to verify setup:
   ```bash
   pytest
   ruff check src tests
   mypy src
   ```

## Rule 0: No Secrets!
Never commit or share real tokens, phone numbers, cookies, session IDs, or private HAR files. Always use fake placeholders in issues, tests, and documentation.

## Pull Request Guidelines
- Follow Conventional Commits for commit messages (`feat:`, `fix:`, `docs:`, etc.).
- Add unit tests for new features or bug fixes.
- Ensure all checks (`pytest`, `ruff`, `mypy`) pass successfully.
