# Contributing to Multi-language OCR API

Thank you for your interest in contributing to the Multi-language OCR API! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Submitting Changes](#submitting-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Documentation](#documentation)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- (Optional) Docker

### Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/g-j4mb/multi-language-ocr-api.git
   cd multi-language-ocr-api
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   make install
   make dev-setup
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the [code style guidelines](#code-style)

3. Write or update tests for your changes

4. Run the test suite:
   ```bash
   make test
   ```

5. Ensure code quality:
   ```bash
   make lint
   make format
   make type-check
   ```

6. Update documentation if needed

7. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

## Submitting Changes

### Pull Request Process

1. Ensure your branch is up to date with the main branch:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request on GitHub with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference to any related issues
   - Screenshots or examples if applicable

4. Wait for review and address any feedback

### Commit Message Guidelines

We follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```
feat: add PDF processing support
fix: resolve memory leak in OCR service
docs: update API documentation
```

## Testing

### Unit Tests

All new code should include comprehensive unit tests. Run tests with:

```bash
make test
```

### Test Coverage

Aim for high test coverage. Check coverage with:

```bash
make test-coverage
```

### Integration Tests

For API changes, test the endpoints manually or add integration tests.

## Code Style

### Python Code

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep line length under 127 characters

### Code Formatting

We use Black for automatic code formatting:

```bash
make format  # Format code
make check-format  # Check if code is properly formatted
```

### Linting

Run linting checks:

```bash
make lint
```

### Type Checking

Use mypy for static type checking:

```bash
make type-check
```

## Documentation

### Code Documentation

- All public functions and classes should have docstrings
- Use Google-style docstrings
- Document parameters, return values, and exceptions

### API Documentation

- Update OpenAPI/Swagger documentation for API changes
- Update README.md for new features or configuration options
- Add examples for new endpoints

### Changelog

Update the CHANGELOG.md file for significant changes following [Keep a Changelog](https://keepachangelog.com/) format.

## Issue Reporting

When reporting bugs or requesting features:

1. Check existing issues first
2. Use issue templates when available
3. Provide detailed information:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Sample files or data if applicable

## Security

If you discover a security vulnerability:

1. Do not create a public issue
2. Email security concerns to: security@example.com
3. Provide detailed information about the vulnerability

## License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

Thank you for contributing to the Multi-language OCR API! 🎉