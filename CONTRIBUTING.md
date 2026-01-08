# Contributing to AI-SRE Platform

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Development Setup

See [README.md](./README.md) for local development setup instructions.

## Code Style

### Python
- Follow PEP 8 style guide
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Type hints required for all functions
- Docstrings required for all modules, classes, and functions

### TypeScript
- Use TypeScript strict mode
- Follow ESLint rules
- Use Prettier for formatting
- Prefer functional components
- Use React Query for data fetching

## Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:
```
feat(agents): add confidence scoring to RCA agent

Implement confidence calculation based on agent agreement
and evidence quality.
```

## Testing

- Write tests for all new features
- Maintain or improve test coverage
- Run tests before committing: `make test`
- Ensure all tests pass in CI

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers
6. Address review comments
7. Squash commits if requested

## Code Review Guidelines

- Be respectful and constructive
- Focus on code, not the person
- Explain reasoning for suggestions
- Approve when satisfied
- Request changes when needed

## Questions?

Open an issue or contact maintainers for help.
