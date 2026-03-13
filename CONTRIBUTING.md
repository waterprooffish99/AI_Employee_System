# Contributing to AI Employee System

First off, thank you for considering contributing to AI Employee System! It's people like you that make AI Employee System such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed and what behavior you expected**
* **Include screenshots if possible**
* **Include environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List some examples of how this enhancement would be used**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include tests for new features
* Update documentation as needed
* Add an entry to the changelog

## Development Setup

### Prerequisites

- Python 3.13+
- UV package manager
- Claude Code CLI
- Obsidian (for vault testing)

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/AI_Employee_System.git
cd AI_Employee_System

# Install dependencies
uv sync

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_bronze_quick.py

# Run Bronze Tier tests
bash test_bronze.sh
```

### Code Style

* **Python**: Follow PEP 8
* **Type Hints**: Use type annotations for all function signatures
* **Docstrings**: Google style for all public functions and classes
* **Line Length**: Maximum 100 characters
* **Imports**: Grouped and sorted (use isort)

Example:

```python
"""
Example module demonstrating code style.
"""

from typing import Optional

from src.utils.audit_logger import get_audit_logger


class ExampleClass:
    """Example class showing code style."""

    def __init__(self, name: str, value: Optional[int] = None):
        """
        Initialize example class.

        Args:
            name: Name of the example
            value: Optional value (default: None)
        """
        self.name = name
        self.value = value

    def process(self) -> bool:
        """
        Process the example.

        Returns:
            True if successful, False otherwise
        """
        return True
```

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types include:
* `feat`: A new feature
* `fix`: A bug fix
* `docs`: Documentation changes
* `style`: Code style changes (formatting, etc.)
* `refactor`: Code refactoring
* `test`: Adding tests
* `chore`: Maintenance tasks

Examples:
```
feat(gold-tier): add Ralph Wiggum loop CLI
fix(silver-tier): resolve Gmail OAuth token refresh issue
docs(readme): update quick start section
refactor(mcp): extract common MCP base class
test(platinum): add cloud/local integration tests
```

## Architecture Decisions

For significant changes, we use Architecture Decision Records (ADRs). If your change involves an architectural decision:

1. Create a new ADR file in `docs/adr/`
2. Follow the ADR template
3. Document the context, decision, and consequences

## Documentation

* **README**: Update if you change functionality
* **Code Comments**: Add comments for complex logic
* **Docstrings**: Required for all public APIs
* **Guides**: Create/update guides in `docs/` for new features

## Security

**Important**: Never commit credentials, API keys, or sensitive information.

* Use environment variables for secrets
* Add sensitive files to `.gitignore`
* Run `scripts/scan_secrets.sh` before committing
* Report security vulnerabilities privately

## Review Process

1. **Automated Checks**: CI runs tests and linters
2. **Code Review**: At least one maintainer reviews
3. **Testing**: Reviewers may request additional tests
4. **Merge**: Maintainer merges after approval

## Questions?

Feel free to open an issue with the `question` label or start a discussion in GitHub Discussions.

---

Thank you for contributing to AI Employee System! 🚀
