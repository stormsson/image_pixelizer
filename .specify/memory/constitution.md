<!--
Sync Impact Report:
Version change: N/A → 1.0.0 (initial constitution)
Modified principles: N/A (new constitution)
Added sections: Core Principles, Code Quality Standards, Development Workflow, Governance
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section will reference GUI-specific principles
  ✅ spec-template.md - No changes needed (generic template)
  ✅ tasks-template.md - No changes needed (generic template)
  ✅ checklist-template.md - No changes needed (generic template)
Follow-up TODOs: None
-->

# Pixelizer Constitution

## Core Principles

### I. Separation of Concerns (MVC/MVP Pattern)

GUI components MUST be separated into distinct layers: Model (data/business logic), View (UI presentation), and Controller/Presenter (coordination). Views MUST NOT contain business logic; Models MUST NOT contain UI code. This separation enables testability, maintainability, and allows UI framework changes without affecting core logic.

**Rationale**: GUI applications are prone to tight coupling between UI and business logic. Enforcing architectural boundaries prevents technical debt and enables independent testing of each layer.

### II. Testability (NON-NEGOTIABLE)

All business logic and non-UI components MUST be unit testable without requiring GUI framework initialization. UI components MUST be testable via integration tests or widget testing frameworks. Tests MUST be written before or alongside implementation (TDD preferred). Code coverage targets: minimum 80% for business logic, 60% for UI components.

**Rationale**: GUI applications are difficult to debug in production. Comprehensive testing prevents regressions and enables confident refactoring. Testable code is inherently better structured.

### III. Code Quality & Standards

All code MUST follow PEP 8 style guidelines. Type hints MUST be used for all function signatures and class attributes (Python 3.9+). Code MUST pass linting (ruff, pylint, or flake8) and formatting (black, autopep8) checks before commit. Maximum function length: 50 lines; maximum class length: 300 lines. Complexity MUST be justified if exceeded.

**Rationale**: Consistent code style reduces cognitive load, enables faster onboarding, and prevents style debates. Type hints improve IDE support and catch errors early.

### IV. Error Handling & User Feedback

All user-facing operations MUST handle errors gracefully with clear, actionable error messages. Exceptions MUST be caught at appropriate boundaries (UI layer for user-facing errors, service layer for business logic errors). Long-running operations MUST provide progress feedback. Critical errors MUST be logged with sufficient context for debugging.

**Rationale**: Poor error handling creates frustrating user experiences. Proper error boundaries prevent application crashes and provide users with actionable information.

### V. Documentation

Public APIs, classes, and complex functions MUST have docstrings (Google or NumPy style). README MUST include setup instructions, dependencies, and basic usage examples. Architecture decisions affecting multiple components MUST be documented. Inline comments MUST explain "why" not "what" (code should be self-documenting).

**Rationale**: Documentation enables maintainability and onboarding. Well-documented code reduces time spent understanding existing functionality.

### VI. GUI Best Practices

UI components MUST be responsive to window resizing. All interactive elements MUST be keyboard accessible. Color choices MUST consider accessibility (WCAG contrast ratios). Loading states MUST be shown for async operations. UI MUST remain responsive during long operations (use threading/async appropriately). Platform-specific UI conventions SHOULD be followed when possible.

**Rationale**: Poor UX leads to user frustration and abandonment. Accessibility ensures the application is usable by all users. Responsive design accommodates different screen sizes and window configurations.

### VII. Dependency Management

Dependencies MUST be pinned to specific versions in requirements.txt or pyproject.toml. Virtual environments MUST be used for development. Dependencies MUST be kept minimal; new dependencies require justification. Security vulnerabilities in dependencies MUST be addressed promptly. Python version MUST be specified and enforced.

**Rationale**: Unpinned dependencies cause "works on my machine" issues and production failures. Minimal dependencies reduce attack surface and maintenance burden.

## Code Quality Standards

### Linting & Formatting

- **Linter**: ruff (preferred) or pylint/flake8
- **Formatter**: black with line length 88-100 characters
- **Type Checking**: mypy (strict mode recommended)
- **Pre-commit hooks**: REQUIRED to enforce linting/formatting before commit

### Code Organization

- **Structure**: `src/` for application code, `tests/` for test code
- **GUI Framework**: Use established frameworks (tkinter, PyQt, PySide, wxPython, or modern alternatives like CustomTkinter)
- **Imports**: Absolute imports preferred; group: stdlib, third-party, local
- **Naming**: Classes PascalCase, functions/variables snake_case, constants UPPER_SNAKE_CASE

### Testing Requirements

- **Framework**: pytest (preferred) or unittest
- **Test Structure**: Mirror source structure in `tests/` directory
- **Test Naming**: `test_<functionality>.py` for files, `test_<behavior>()` for functions
- **Fixtures**: Use pytest fixtures for common setup/teardown
- **Mocking**: Use unittest.mock or pytest-mock for external dependencies

## Development Workflow

### Version Control

- **Branching**: Feature branches from `main`; descriptive branch names
- **Commits**: Atomic commits with clear messages; reference issue numbers if applicable
- **Pull Requests**: Required for `main` branch; must pass CI checks (linting, tests)
- **Code Review**: At least one approval required; reviewers verify constitution compliance

### Quality Gates

Before merging to `main`:
1. All tests MUST pass
2. Linting MUST pass with zero errors
3. Type checking MUST pass (warnings acceptable if documented)
4. Code review MUST be completed
5. Constitution compliance MUST be verified

### CI/CD

- Automated testing on all pull requests
- Automated linting and type checking
- Automated security scanning of dependencies
- Build verification for target platforms

## Governance

This constitution supersedes all other coding practices and style guides. All code contributions MUST comply with these principles. Amendments to this constitution require:

1. **Documentation**: Clear rationale for the change
2. **Approval**: Consensus from project maintainers
3. **Migration Plan**: If the change affects existing code, a migration strategy must be provided
4. **Version Update**: Constitution version MUST be incremented per semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles or significant expansions
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements

All pull requests and code reviews MUST verify constitution compliance. Complexity or principle violations MUST be justified in code comments or design documents. When in doubt, prefer simplicity and testability.

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
