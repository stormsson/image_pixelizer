# Implementation Plan: Alternative Background Removal Method

**Branch**: `003-alternative-background-removal` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-alternative-background-removal/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add an alternative automatic background removal method using OpenAI's Vision API (GPT-4 Vision model) that provides a one-click, no-interaction background removal option. This complements the existing interactive point-based method by offering speed and convenience. The implementation includes an autonomous service class that can be used independently of the application, supports both file path and image content inputs, and optionally saves results to file. Environment variable configuration for API key management with .env and .env.sample files.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: OpenAI Python SDK (openai>=1.0.0), python-dotenv (already in requirements.txt), Pillow (PIL) for image I/O, NumPy for pixel data handling  
**Storage**: File system (optional save to file path), in-memory image data processing  
**Testing**: pytest for unit tests, pytest-qt for integration with existing GUI tests. Coverage targets: 80% for business logic (OpenAI service class), integration tests for API interaction (mocked).  
**Target Platform**: Desktop (Windows, macOS, Linux) - same as main application  
**Project Type**: Feature addition to existing desktop GUI application  
**Performance Goals**: Automatic background removal completes within 5 seconds for images up to 2000x2000px (per spec SC-001)  
**Constraints**: Requires OpenAI API key (user must configure), API rate limits and costs apply, internet connection required, maximum image size 2000x2000px (per existing constraints)  
**Scale/Scope**: Single service class addition (~200-300 lines), UI button addition, environment configuration, ~3-5 test files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Pixelizer Constitution principles:

- **Separation of Concerns**: ✅ Design will create an autonomous `OpenAIBackgroundRemover` service class that is independent of the GUI application. The class will handle OpenAI API communication, image format conversion, and optional file saving. Integration with existing `MainController` will follow the same pattern as existing `BackgroundRemover` service.

- **Testability**: ✅ The `OpenAIBackgroundRemover` class will be a pure service class testable without PySide6. API calls will be mockable for unit tests. Business logic (image format conversion, API request construction, response parsing) will have 80%+ coverage target. Integration tests will verify API interaction patterns (with mocked API responses).

- **Code Quality**: ✅ Code will follow PEP 8, use type hints throughout, pass ruff linting and black formatting. Function/class length limits will be enforced. Error handling will be comprehensive.

- **Error Handling**: ✅ Error boundaries defined: API key missing/invalid errors caught with user-friendly messages, API rate limit errors handled gracefully, network errors handled with retry logic or clear error messages, invalid image inputs validated.

- **Documentation**: ✅ Public API (OpenAIBackgroundRemover class) will have Google-style docstrings. Environment variable configuration documented. Architecture decisions documented in research.md and code comments.

- **GUI Best Practices**: ✅ UI integration follows existing patterns: button in controls panel, QThread for background processing to maintain UI responsiveness, signal/slot for updates, error messages displayed to user. Same UI disable/enable pattern as existing background removal.

- **Dependencies**: ✅ Minimal new dependencies: OpenAI Python SDK (openai>=1.0.0). python-dotenv already in requirements.txt. All versions will be pinned in requirements.txt.

**Violations**: None identified. Design complies with all constitution principles.

### Post-Design Constitution Check

*Re-checked after Phase 1 design completion.*

All principles remain compliant:

- **Separation of Concerns**: ✅ `OpenAIBackgroundRemover` is an autonomous service class with no GUI dependencies. Can be used independently. Integration with controller follows existing service patterns.

- **Testability**: ✅ Service class is pure and testable. API calls mockable. Comprehensive test coverage planned for business logic and API interaction patterns.

- **Code Quality**: ✅ Type hints, linting, formatting standards maintained. Error handling comprehensive.

- **Error Handling**: ✅ Error boundaries defined in contracts: API key validation, network errors, rate limits, invalid inputs all handled with user-friendly messages.

- **Documentation**: ✅ Service contract includes comprehensive docstrings. Environment configuration documented. Architecture documented in research.md.

- **GUI Best Practices**: ✅ Follows existing patterns: QThread for processing, signal/slot for updates, UI disable/enable during processing. Button placement consistent with existing controls.

- **Dependencies**: ✅ Minimal: OpenAI SDK only. python-dotenv already present.

**Final Status**: ✅ All constitution principles satisfied. Ready for implementation.

## Project Structure

### Documentation (this feature)

```text
specs/003-alternative-background-removal/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── services/
│   ├── __init__.py
│   ├── background_remover.py         # Existing interactive method (rembg)
│   └── openai_background_remover.py  # NEW: OpenAI API-based automatic method
├── controllers/
│   └── main_controller.py            # MODIFIED: Add automatic background removal method
└── views/
    └── controls_panel.py             # MODIFIED: Add "Remove Background (Automatic)" button

.env.sample                            # NEW: Template for environment variables
.env                                   # MODIFIED: User adds OPENAI_API_KEY (gitignored)

requirements.txt                       # MODIFIED: Add openai>=1.0.0

tests/
├── unit/
│   └── test_openai_background_remover.py  # NEW: Unit tests for OpenAI service
└── integration/
    └── test_openai_integration.py         # NEW: Integration tests (mocked API)
```

**Structure Decision**: Add new autonomous service class `OpenAIBackgroundRemover` that follows the same pattern as existing `BackgroundRemover` but uses OpenAI API instead of rembg. The class is designed to be usable independently of the application. Integration with existing controller and views follows established patterns. Environment configuration uses .env files with .env.sample template.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified.

