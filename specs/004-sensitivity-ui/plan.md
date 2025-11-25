# Implementation Plan: Sensitivity Dropdown for K-Means Bins

**Branch**: `004-sensitivity-ui` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-sensitivity-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace the existing sensitivity slider (0-100, converted to 0.0-1.0 float) with a dropdown menu that displays powers of 2 (4, 8, 16, 32, 64, 128, 256) plus "None" to directly configure k-means bin counts. The dropdown resets to "None" when a new image is loaded and is disabled during image processing. This provides users with direct, predictable control over color reduction granularity.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PySide6 (Qt framework), numpy, opencv-python (cv2 for k-means)  
**Storage**: N/A (in-memory settings model)  
**Testing**: pytest, pytest-qt for GUI testing  
**Target Platform**: Desktop (cross-platform via PySide6)  
**Project Type**: Single desktop GUI application (MVC architecture)  
**Performance Goals**: Dropdown value changes should trigger color reduction with <2s response time for typical images  
**Constraints**: Must maintain MVC separation, all changes must be unit testable, UI must remain responsive during processing  
**Scale/Scope**: Single feature modification affecting 3-4 files (view, model, controller, tests)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Pixelizer Constitution principles:

- **Separation of Concerns**: ✅ Design maintains MVC: View (dropdown in ControlsPanel), Model (ColorReductionSettings stores bin_count), Controller (MainController coordinates). UI logic separated from business logic.
- **Testability**: ✅ Business logic (settings model, controller) testable without GUI. UI component (dropdown) testable via pytest-qt. Existing test infrastructure supports this.
- **Code Quality**: ✅ Code follows PEP 8, uses type hints (Python 3.11+), passes ruff/black linting. Changes are localized and maintain existing patterns.
- **Error Handling**: ✅ Dropdown changes handled in controller with error signals. Invalid states prevented by dropdown constraints (only valid options available).
- **Documentation**: ✅ Public methods have docstrings. Settings model changes documented. Architecture changes minimal and localized.
- **GUI Best Practices**: ✅ Dropdown disabled during processing (prevents invalid state). UI remains responsive. Accessibility maintained (keyboard navigation, screen readers).
- **Dependencies**: ✅ No new dependencies required. Uses existing PySide6 QComboBox widget.

**Violations**: None. Design fully complies with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/004-sensitivity-ui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── controls-panel.md
│   └── main-controller.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── settings_model.py          # Update ColorReductionSettings: sensitivity → bin_count
├── views/
│   └── controls_panel.py          # Replace slider/spinbox with QComboBox dropdown
├── controllers/
│   └── main_controller.py         # Update update_sensitivity → update_bin_count
└── services/
    └── color_reducer.py            # Already supports k parameter (no changes needed)

tests/
├── unit/
│   ├── test_settings_model.py     # Update tests for bin_count
│   └── test_main_controller.py   # Update tests for bin_count
└── gui/
    └── test_controls_panel.py      # Update tests for dropdown
```

**Structure Decision**: Single project structure maintained. Changes are localized to existing MVC components. No new modules or services required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Design is straightforward and maintains existing architecture patterns.
