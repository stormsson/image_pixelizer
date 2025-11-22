# Implementation Plan: Image Operations in Controls Panel

**Branch**: `002-image-operations` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-image-operations/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add image operation buttons to the controls panel, starting with "Remove Background" functionality using interactive point selection with the rembg AI model (SAM support), and an "Undo" button that tracks complex button-based operations (not slider changes). The implementation extends the existing pixelizer application by adding interactive point selection mode where users click on the image to mark areas as "keep" (foreground) or "remove" (background) using left-click and right-click respectively. Users select points with visual feedback (green markers for keep, red markers for remove), then click "Apply" to process background removal, or "Cancel" to exit without applying. The implementation includes new service classes for background removal with SAM prompt support, operation history management, point selection state management, new UI buttons in the controls panel (Remove Background, Apply, Cancel, Undo), image view modifications for click handling and visual markers, and integration with the existing controller to coordinate the interactive workflow. All operations must maintain UI responsiveness and preserve slider-based changes (pixelization/color reduction) when undo is applied.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PySide6 (Qt6 bindings), Pillow (PIL) for image processing, NumPy for efficient pixel manipulation, rembg for AI-powered background removal with SAM model support, onnxruntime for SAM model inference  
**Storage**: File system (save processed images as PNG files; no database or persistent state required). Operation history and point selection state maintained in memory during session.  
**Testing**: pytest for unit tests, pytest-qt for PySide6 widget testing. Coverage targets: 80% for business logic (models, services), 60% for UI components. All tests must pass before merge to main branch.  
**Target Platform**: Desktop (Windows, macOS, Linux)  
**Project Type**: single (desktop GUI application)  
**Performance Goals**: Background removal operation completes within 5 seconds for images up to 2000x2000px after user clicks "Apply". Point selection interaction is immediate (no processing delay). Undo operation completes within 1 second. UI remains responsive during background removal processing.  
**Constraints**: Maximum image size 2000x2000px (per existing spec), maintain UI responsiveness during processing (use threading for rembg operations), memory-efficient operation history (max 20 operations), undo only tracks complex button-based operations (not slider changes), point selection coordinates must be captured relative to displayed image (accounting for scaling/positioning)  
**Scale/Scope**: Extension to existing pixelizer application, 2 user stories, ~4-6 new source files (including PointSelection model), new buttons in controls panel (Remove Background, Apply, Cancel, Undo), interactive point selection with visual markers, operation history management, and comprehensive test suite (~6-9 new test files)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Pixelizer Constitution principles:

- **Separation of Concerns**: ✅ Design will extend existing MVC architecture. Background removal logic will be in a separate service class (BackgroundRemover), operation history will be managed in a service class (OperationHistoryManager), point selection state will be managed separately from UI rendering, isolated from UI code. UI buttons will be added to existing ControlsPanel view. Image view will handle click events and visual marker rendering, but point selection logic remains in controller/service layer.

- **Testability**: ✅ Background removal service will be testable without PySide6 (can test rembg integration independently). Operation history management will be pure Python classes testable without GUI. UI button components will be testable via pytest-qt. Business logic will have 80%+ coverage target. All new services and models will have pytest unit tests. GUI components will have pytest-qt integration tests.

- **Code Quality**: ✅ Code will follow PEP 8, use type hints throughout, pass ruff linting and black formatting. Function/class length limits will be enforced. New code will match existing codebase style.

- **Error Handling**: ✅ Error boundaries defined: rembg processing errors caught at service layer with user-friendly messages, operation history errors handled gracefully. Invalid undo attempts (no history) handled with disabled button state.

- **Documentation**: ✅ Public APIs (BackgroundRemover service, OperationHistoryManager, new model classes) will have Google-style docstrings. Architecture decisions documented in code comments.

- **GUI Best Practices**: ✅ UI will remain responsive during background removal (use QThread for rembg processing). Buttons will be keyboard accessible. Loading states shown during background removal. Button states (enabled/disabled) clearly indicate availability. Point selection mode will have clear visual indicators (green/red markers). Click handling will account for image scaling and positioning. Apply/Cancel buttons provide clear workflow control.

- **Dependencies**: ✅ New dependencies: rembg (AI background removal with SAM support), onnxruntime (required by rembg for SAM model). Justified: required for core feature functionality with interactive point selection. Versions will be pinned in requirements.txt or pyproject.toml. All other dependencies remain minimal.

**Violations**: None identified. Design complies with all constitution principles.

### Post-Design Constitution Check

*Re-checked after Phase 1 design completion.*

All principles remain compliant:

- **Separation of Concerns**: ✅ BackgroundRemover service isolated from UI. OperationHistoryManager manages state separately. Controller coordinates without containing business logic.

- **Testability**: ✅ All new services are pure functions/classes testable without PySide6. Models are data classes easily testable. UI components testable via pytest-qt. Comprehensive test suite covers all new entities and services.

- **Code Quality**: ✅ Type hints used throughout. Code structure follows PEP 8. Linting/formatting tools specified.

- **Error Handling**: ✅ Error boundaries defined in contracts: BackgroundRemover validates and provides user-friendly error messages. Controller catches exceptions and emits error signals. Views display errors to users.

- **Documentation**: ✅ All service contracts include docstrings. Architecture documented in research.md and data-model.md.

- **GUI Best Practices**: ✅ Qt layouts for responsiveness, QThread for background processing, signal/slot for updates. Button accessibility via Qt's built-in support.

- **Dependencies**: ✅ Minimal new dependency: rembg. All versions pinned in requirements.txt.

**Final Status**: ✅ All constitution principles satisfied. Ready for implementation.

## Project Structure

### Documentation (this feature)

```text
specs/002-image-operations/
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
├── models/
│   ├── image_model.py          # Existing - no changes
│   ├── settings_model.py       # Existing - no changes
│   └── point_selection.py      # NEW - PointSelection model (x, y, label: keep/remove)
├── services/
│   ├── image_loader.py         # Existing - no changes
│   ├── image_saver.py          # Existing - no changes
│   ├── pixelizer.py            # Existing - no changes
│   ├── color_reducer.py        # Existing - no changes
│   ├── background_remover.py   # MODIFIED - add SAM prompt support for point-based removal
│   └── operation_history.py    # NEW - manages undo history (max 20 operations)
├── views/
│   ├── main_window.py          # MODIFIED - signal connections for point selection workflow
│   ├── image_view.py           # MODIFIED - add click handling, visual markers (green/red), point selection mode
│   ├── controls_panel.py       # MODIFIED - add Remove Background, Apply, Cancel, and Undo buttons
│   └── status_bar.py           # Existing - no changes
└── controllers/
    └── main_controller.py      # MODIFIED - add point selection state management, background removal with prompts, undo methods

tests/
├── unit/
│   ├── test_background_remover.py    # MODIFIED - add tests for SAM prompt support
│   ├── test_operation_history.py     # NEW - tests for OperationHistoryManager
│   └── test_point_selection.py      # NEW - tests for PointSelection model
├── integration/
│   └── test_image_operations.py      # MODIFIED - add tests for interactive point selection workflow
└── gui/
    ├── test_controls_panel_operations.py  # MODIFIED - add tests for Apply/Cancel buttons
    └── test_image_view_point_selection.py # NEW - tests for click handling and visual markers
```

**Structure Decision**: Single project structure extending existing pixelizer application. New services (BackgroundRemover with SAM support, OperationHistoryManager) follow existing service pattern. New model (PointSelection) for point selection data. New UI buttons added to existing ControlsPanel (Remove Background, Apply, Cancel, Undo). ImageView modified to handle click events and render visual markers. Controller extended to coordinate point selection state, background removal with prompts, and undo operations. This structure maintains consistency with existing codebase and enables independent testing of each layer. Point selection state is managed in controller, visual rendering in view, and business logic in services.

## Key Technical Decisions

### Interactive Point Selection Implementation

**Decision**: Use SAM model with rembg for point-based background removal

**Rationale**:
- SAM (Segment Anything Model) supports point prompts for precise control
- rembg library provides SAM integration with simple API
- Point-based selection gives users control over what to keep/remove
- Visual feedback (green/red markers) provides clear indication of selected points

**Implementation Details**:
- Point selection mode entered when "Remove Background" button clicked
- Left-click creates "keep" point (green marker), right-click creates "remove" point (red marker)
- Points stored in PointSelectionCollection managed by controller
- Coordinates converted from view space to image pixel space (accounting for scaling)
- Apply button converts points to SAM prompt format and processes background removal
- Cancel button exits mode and clears all points

**Coordinate Conversion**:
- ImageView must track image scaling and positioning
- Click coordinates in view space converted to image pixel coordinates
- Conversion formula: `image_x = (view_x - offset_x) / scale_factor`
- Ensures points are correctly positioned regardless of how image is displayed

**Visual Markers**:
- Green circles for "keep" points (foreground)
- Red circles for "remove" points (background)
- Markers rendered on top of image using QPainter or overlay widget
- Markers removed when point selection mode exits

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified.
