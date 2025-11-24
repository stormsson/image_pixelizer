# Implementation Plan: Photographic Editing Tools

**Branch**: `004-photo-editing-tools` | **Date**: 2025-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-photo-editing-tools/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add photographic editing tools accessible from the main menu, with each tool opening in a separate window. The first tool is Image Levels, which displays a histogram of tonal distribution and provides two sliders (Lights Cutoff and Darks Cutoff) to adjust the image's tonal range by clipping highlights and shadows. The implementation follows the existing MVC pattern, with a new service class for levels adjustment, a new window class for the tool interface, and integration with the main menu and controller.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PySide6 (GUI framework), NumPy (image processing), Pillow (PIL) for image I/O  
**Storage**: In-memory image data processing, no persistent storage required  
**Testing**: pytest for unit tests, pytest-qt for GUI component tests. Coverage targets: 80% for business logic (levels service), 60% for UI components (tool window)  
**Target Platform**: Desktop (Windows, macOS, Linux) - same as main application  
**Project Type**: Feature addition to existing desktop GUI application  
**Performance Goals**: Histogram calculation completes within 2 seconds for images up to 2000x2000px (per spec SC-002), slider adjustments update display in real-time with <100ms delay (per spec SC-003)  
**Constraints**: Maximum image size 2000x2000px (per existing constraints), must maintain UI responsiveness during processing, must integrate with existing undo/redo system  
**Scale/Scope**: Single service class addition (~200-300 lines), one tool window class (~300-400 lines), menu integration, ~3-5 test files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Pixelizer Constitution principles:

- **Separation of Concerns**: ✅ Design will create a `LevelsAdjuster` service class that is independent of the GUI application. The class will handle histogram calculation and levels adjustment logic. Integration with existing `MainController` will follow the same pattern as existing services. The tool window will be a separate view class that communicates with the controller via signals/slots.

- **Testability**: ✅ The `LevelsAdjuster` class will be a pure service class testable without PySide6. Business logic (histogram calculation, levels adjustment) will have 80%+ coverage target. The tool window will be testable via pytest-qt.

- **Code Quality**: ✅ Code will follow PEP 8, use type hints throughout, pass ruff linting and black formatting. Function/class length limits will be enforced. Error handling will be comprehensive.

- **Error Handling**: ✅ Error boundaries defined: invalid image inputs validated, slider value validation, histogram calculation errors handled gracefully with user-friendly messages.

- **Documentation**: ✅ Public API (LevelsAdjuster class, tool window class) will have Google-style docstrings. Architecture decisions documented in research.md and code comments.

- **GUI Best Practices**: ✅ UI integration follows existing patterns: separate window for tool, QThread for background processing if needed, signal/slot for updates, error messages displayed to user. Real-time updates maintain UI responsiveness.

- **Dependencies**: ✅ No new dependencies required - uses existing PySide6, NumPy, and Pillow. All versions already pinned in requirements.txt.

**Violations**: None identified. Design complies with all constitution principles.

### Post-Design Constitution Check

*Re-checked after Phase 1 design completion.*

All principles remain compliant:

- **Separation of Concerns**: ✅ `LevelsAdjuster` is an autonomous service class with no GUI dependencies. Can be used independently. Integration with controller follows existing service patterns.

- **Testability**: ✅ Service class is pure and testable. Comprehensive test coverage planned for business logic and GUI components.

- **Code Quality**: ✅ Type hints, linting, formatting standards maintained. Error handling comprehensive.

- **Error Handling**: ✅ Error boundaries defined in contracts: invalid inputs, calculation errors all handled with user-friendly messages.

- **Documentation**: ✅ Service contract includes comprehensive docstrings. Architecture documented in research.md.

- **GUI Best Practices**: ✅ Follows existing patterns: separate window, signal/slot for updates, real-time preview. Maintains UI responsiveness.

- **Dependencies**: ✅ No new dependencies required.

**Final Status**: ✅ All constitution principles satisfied. Ready for implementation.

## Project Structure

### Documentation (this feature)

```text
specs/004-photo-editing-tools/
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
│   └── levels_adjuster.py  # NEW: Levels adjustment service
├── views/
│   └── levels_window.py     # NEW: Image Levels tool window
├── controllers/
│   └── main_controller.py  # MODIFIED: Add levels adjustment method
└── models/
    └── image_model.py       # UNCHANGED: Uses existing ImageModel

tests/
├── unit/
│   └── test_levels_adjuster.py  # NEW: Unit tests for service
└── gui/
    └── test_levels_window.py    # NEW: GUI tests for tool window
```

**Structure Decision**: Add new autonomous service class `LevelsAdjuster` that follows the same pattern as existing services (`ColorReducer`, `Pixelizer`). The tool window `LevelsWindow` follows the same pattern as `MainWindow` but is a separate QMainWindow instance. Integration with existing controller and views follows established patterns. Menu integration extends the existing menu bar structure in `MainWindow`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified.
