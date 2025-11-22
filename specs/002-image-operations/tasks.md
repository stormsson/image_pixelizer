# Tasks: Image Operations in Controls Panel

**Input**: Design documents from `/specs/002-image-operations/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per existing codebase standards. Each meaningful entity and feature must have pytest tests. Unit tests for models and services, pytest-qt tests for GUI components, and integration tests for end-to-end workflows. Coverage targets: 80% for business logic, 60% for UI components.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 Add rembg dependency to pyproject.toml or requirements.txt with pinned version
- [X] T002 [P] Update project documentation to include rembg dependency and installation instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Create BackgroundRemovalError exception class in src/services/__init__.py
- [X] T004 [P] Create OperationHistoryEntry dataclass in src/services/operation_history.py with operation_type, image_state, timestamp attributes
- [X] T005 [P] Create PointSelection dataclass in src/models/point_selection.py with x, y, label (keep/remove) attributes and validation

### Tests for Foundational Components

> **NOTE: Write these tests to verify models work correctly before proceeding**

- [X] T050 [P] Write unit tests for OperationHistoryEntry in tests/unit/test_operation_history.py (validation, operation_type, image_state, timestamp)
- [X] T051 [P] Write unit tests for BackgroundRemovalError in tests/unit/test_background_remover.py (exception creation, user_message attribute)
- [X] T052 [P] Write unit tests for PointSelection in tests/unit/test_point_selection.py (coordinate validation, label validation, keep/remove labels)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Remove Background Operation (Priority: P1) 🎯 MVP

**Goal**: Users can click "Remove Background" button to enter interactive point selection mode, click points on the image (left-click = keep, right-click = remove), then click "Apply" to remove backgrounds based on selected points, making them transparent while preserving the main subject

**Independent Test**: Load an image, click "Remove Background" button, click points on the image (left-click for keep, right-click for remove), click "Apply", verify the background becomes transparent (or is removed) while the foreground subject remains visible. The operation should complete within a reasonable time and the result should be visually apparent.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T053 [P] [US1] Write unit tests for BackgroundRemover service with SAM prompts in tests/unit/test_background_remover.py (remove_background with prompts, SAM prompt format conversion, point-based removal, error handling)
- [ ] T054 [P] [US1] Write pytest-qt tests for Remove Background, Apply, and Cancel buttons in tests/gui/test_controls_panel_operations.py (button visibility, enabled/disabled states, signal emissions, point selection mode)
- [ ] T055 [P] [US1] Write pytest-qt tests for point selection click handling in tests/gui/test_image_view_point_selection.py (left-click keep, right-click remove, coordinate conversion, visual markers)
- [ ] T056 [US1] Write integration test for interactive point selection workflow in tests/integration/test_image_operations.py (load → enter point selection → click points → apply → verify result, use data/sample.jpg)
- [ ] T057 [P] [US1] Write pytest-qt tests for UI disable/enable during background removal in tests/gui/test_main_window_ui_state.py (UI disabled when processing starts, UI enabled when processing completes, all controls disabled during processing)

### Implementation for User Story 1

#### Point Selection State Management

- [X] T006 [US1] Create PointSelectionCollection class in src/models/point_selection.py with add_point, clear, get_keep_points, get_remove_points, to_sam_prompts methods
- [X] T007 [US1] Implement point selection state management in src/controllers/main_controller.py (enter_point_selection_mode, exit_point_selection_mode, add_point, clear_points methods)
- [X] T008 [US1] Add point_selection_mode_active signal in src/controllers/main_controller.py to notify views when point selection mode changes
- [X] T009 [US1] Add point_added signal in src/controllers/main_controller.py to notify views when points are added (for visual marker updates)

#### BackgroundRemover Service Updates

- [X] T010 [US1] Update BackgroundRemover service in src/services/background_remover.py to use SAM model (new_session('sam')) instead of default u2net
- [X] T011 [US1] Update remove_background method in src/services/background_remover.py to accept prompts parameter (List[Dict[str, Any]]) for SAM point prompts
- [X] T012 [US1] Implement SAM prompt format conversion in src/services/background_remover.py (convert PointSelection list to rembg SAM prompt format: [{"type": "point", "data": [x, y], "label": 1/0}])
- [X] T013 [US1] Update background removal error handling in src/services/background_remover.py for SAM model initialization errors and prompt processing errors

#### ImageView Click Handling and Visual Markers

- [X] T014 [US1] Add point selection mode state tracking in src/views/image_view.py (is_point_selection_mode boolean flag)
- [X] T015 [US1] Implement mousePressEvent override in src/views/image_view.py to handle left-click (keep) and right-click (remove) during point selection mode
- [X] T016 [US1] Implement coordinate conversion in src/views/image_view.py (convert view click coordinates to image pixel coordinates, accounting for scaling and positioning)
- [X] T017 [US1] Emit point_clicked signal from src/views/image_view.py with x, y, and button type (left/right) when clicks occur during point selection mode
- [X] T018 [US1] Implement visual marker rendering in src/views/image_view.py (green circles for keep points, red circles for remove points) using QPainter in paintEvent
- [X] T019 [US1] Add update_point_markers method in src/views/image_view.py to update visual markers when points are added/removed
- [X] T020 [US1] Implement clear_markers method in src/views/image_view.py to remove all visual markers when point selection mode exits

#### Controls Panel Buttons

- [X] T021 [US1] Add "Remove Background" button to ControlsPanel in src/views/controls_panel.py with remove_background_requested signal
- [X] T022 [US1] Add "Apply" button to ControlsPanel in src/views/controls_panel.py with apply_requested signal (initially disabled/hidden)
- [X] T023 [US1] Add "Cancel" button to ControlsPanel in src/views/controls_panel.py with cancel_requested signal (initially disabled/hidden)
- [X] T024 [US1] Implement button visibility/enabled state management in src/views/controls_panel.py (Apply enabled when points selected, Cancel visible during point selection mode)
- [X] T025 [US1] Add set_point_selection_mode method in src/views/controls_panel.py to update button states based on point selection mode
- [X] T026 [US1] Add update_apply_button_state method in src/views/controls_panel.py to enable/disable Apply button based on point count

#### Controller Integration

- [X] T027 [US1] Connect Remove Background button signal to enter_point_selection_mode in src/views/main_window.py
- [X] T028 [US1] Connect Apply button signal to apply_background_removal in src/views/main_window.py
- [X] T029 [US1] Connect Cancel button signal to cancel_point_selection in src/views/main_window.py
- [X] T030 [US1] Connect point_clicked signal from ImageView to add_point in controller in src/views/main_window.py
- [X] T031 [US1] Connect point_selection_mode_active signal from controller to set_point_selection_mode in controls panel in src/views/main_window.py
- [X] T032 [US1] Connect point_added signal from controller to update_point_markers in image view in src/views/main_window.py
- [X] T033 [US1] Connect point_added signal from controller to update_apply_button_state in controls panel in src/views/main_window.py
- [X] T034 [US1] Implement apply_background_removal method in src/controllers/main_controller.py to convert points to SAM prompts, call BackgroundRemover with prompts, update ImageModel, and emit signals
- [X] T035 [US1] Implement cancel_point_selection method in src/controllers/main_controller.py to clear points, exit point selection mode, and emit signals
- [X] T036 [US1] Add BackgroundRemover service initialization with SAM model in src/controllers/main_controller.py constructor
- [X] T037 [US1] Implement QThread worker for background removal processing with prompts in src/controllers/main_controller.py to maintain UI responsiveness
- [X] T038 [US1] Update main window to call set_image_loaded on controls panel when image_loaded/image_updated signals are received
- [X] T039 [US1] Add processing_started signal in src/controllers/main_controller.py to notify views when background removal processing begins
- [X] T040 [US1] Add processing_finished signal in src/controllers/main_controller.py to notify views when background removal processing completes (success or error)
- [X] T041 [US1] Emit processing_started signal in apply_background_removal method in src/controllers/main_controller.py when thread starts
- [X] T042 [US1] Emit processing_finished signal in _on_background_removal_complete and _on_background_removal_error methods in src/controllers/main_controller.py when processing completes
- [X] T043 [US1] Implement set_ui_enabled method in src/views/main_window.py to enable/disable all UI controls (controls panel, image view interactions, menu actions)
- [X] T044 [US1] Connect processing_started signal from controller to set_ui_enabled(False) in src/views/main_window.py
- [X] T045 [US1] Connect processing_finished signal from controller to set_ui_enabled(True) in src/views/main_window.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - users can enter point selection mode, click points on the image, apply background removal based on selected points, and the UI is properly disabled during processing and restored when complete

---

## Phase 4: User Story 2 - Undo Operation (Priority: P2)

**Goal**: Users can click "Undo" button to revert the last complex operation (like background removal), preserving slider-based changes that were applied before that operation

**Independent Test**: Load an image, apply the "Remove Background" operation, then click "Undo" and verify the image reverts to its previous state (before background removal). The undo should work correctly and restore the exact previous image state, preserving any slider adjustments.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T057 [P] [US2] Write unit tests for OperationHistoryManager service in tests/unit/test_operation_history.py (add_operation, can_undo, get_last_operation, pop_last_operation, clear, get_count, rolling history limit, validation)
- [ ] T058 [P] [US2] Write pytest-qt tests for Undo button in tests/gui/test_controls_panel_operations.py (button visibility, enabled/disabled states, signal emissions)
- [ ] T059 [US2] Write integration test for undo workflow in tests/integration/test_image_operations.py (load → remove background → undo → verify restoration, slider preservation)

### Implementation for User Story 2

- [X] T039 [US2] Implement OperationHistoryManager service in src/services/operation_history.py with add_operation, can_undo, get_last_operation, pop_last_operation, clear, get_count methods
- [X] T040 [US2] Implement rolling history management in src/services/operation_history.py (max 20 operations, remove oldest when limit reached)
- [X] T041 [US2] Add "Undo" button to ControlsPanel in src/views/controls_panel.py with undo_requested signal
- [X] T042 [US2] Implement undo button visibility control in src/views/controls_panel.py (disabled when no operations available, enabled when operations exist)
- [X] T043 [US2] Add update_undo_state method in src/views/controls_panel.py to update undo button enabled state based on operation history
- [X] T044 [US2] Add OperationHistoryManager initialization in src/controllers/main_controller.py constructor
- [X] T045 [US2] Implement undo_operation method in src/controllers/main_controller.py to restore image state from history and reapply slider settings
- [X] T046 [US2] Implement operation history tracking in src/controllers/main_controller.py (add entry before applying complex operations in apply_background_removal)
- [X] T047 [US2] Implement slider preservation logic in src/controllers/main_controller.py (reapply pixelization/color reduction after undo)
- [X] T048 [US2] Implement clear_history method in src/controllers/main_controller.py to clear operation history when new image is loaded
- [X] T049 [US2] Connect undo button signal to controller in src/views/main_window.py
- [X] T050 [US2] Connect operation_history_changed signal from controller to controls panel update in src/views/main_window.py
- [X] T051 [US2] Update load_image method in src/controllers/main_controller.py to clear operation history when new image is loaded
- [X] T052 [US2] Implement real-time image update in src/views/image_view.py when undo is applied

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can remove backgrounds and undo operations

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T060 [P] Add docstrings to all new public APIs (BackgroundRemover, OperationHistoryManager, PointSelection, PointSelectionCollection) following Google style
- [ ] T061 [P] Add type hints throughout new codebase (rembg types, operation history types, point selection types, SAM prompt types)
- [ ] T062 Code cleanup and refactoring to ensure PEP 8 compliance for new code
- [ ] T063 [P] Improve error messages across all new user-facing operations (point selection, background removal, undo)
- [ ] T064 [P] Add keyboard shortcuts for Remove Background, Apply, Cancel, and Undo buttons (if applicable)
- [ ] T065 Validate all edge cases from spec.md are handled (transparent backgrounds, complex backgrounds, history limits, point selection edge cases, coordinate conversion edge cases, etc.)
- [ ] T066 Run quickstart.md validation to ensure user workflow matches implementation
- [ ] T067 [P] Verify test coverage meets targets (80% business logic, 60% UI) using pytest-cov for new code
- [ ] T068 [P] Add test fixtures and helpers in tests/conftest.py for rembg testing (mock rembg, SAM model mocking, sample images with backgrounds, fixture for data/sample.jpg, point selection test helpers)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 5)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - Requires PointSelection model from Foundational phase
  - Point selection state management must be complete before UI integration
  - BackgroundRemover SAM support must be complete before Apply button functionality
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 (needs complex operations to undo)

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation (TDD approach)
- Models before services
- Services before views/controllers
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002)
- All Foundational tasks marked [P] can run in parallel (T004, T005)
- Once Foundational phase completes:
  - US1 and US2 can be worked on sequentially (US2 depends on US1)
  - Within US1, tasks marked [P] can run in parallel:
    - Point selection model and tests (T006, T052)
    - BackgroundRemover updates and tests (T010-T013, T053)
    - ImageView click handling and visual markers (T014-T020, T055)
    - Controls panel buttons (T021-T026, T054)
- Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Tests can be created in parallel:
Task: "Write unit tests for BackgroundRemover service with SAM prompts in tests/unit/test_background_remover.py"
Task: "Write pytest-qt tests for point selection click handling in tests/gui/test_image_view_point_selection.py"
Task: "Write pytest-qt tests for Remove Background, Apply, Cancel buttons in tests/gui/test_controls_panel_operations.py"

# Point selection model and BackgroundRemover updates can be developed in parallel:
Task: "Create PointSelectionCollection class in src/models/point_selection.py"
Task: "Update BackgroundRemover service to use SAM model in src/services/background_remover.py"

# ImageView click handling and Controls panel can be developed in parallel (after models):
Task: "Implement mousePressEvent and visual markers in src/views/image_view.py"
Task: "Add Apply and Cancel buttons to ControlsPanel in src/views/controls_panel.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (background removal)
   - Developer B: Can prepare User Story 2 (undo) but must wait for US1 completion
3. After US1 complete:
   - Developer A: User Story 2 (undo)
   - Developer B: Polish and testing
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks include exact file paths for clarity
- Background removal requires rembg library with SAM support and onnxruntime installation (handled in Setup phase)
- Point selection requires interactive clicking on image (left-click = keep, right-click = remove)
- Visual markers (green for keep, red for remove) provide feedback during point selection
- Apply button confirms point selection and processes background removal
- Cancel button exits point selection mode without applying changes
- Coordinate conversion required: view click coordinates must be converted to image pixel coordinates
- SAM model used for point-based background removal (requires prompts in rembg format)
- Operation history is in-memory only (no persistence across app restarts)
- Undo only tracks complex button-based operations, NOT slider changes
- Slider states are preserved and reapplied after undo operations
- QThread is used for background removal to maintain UI responsiveness
- Sample image for testing background removal is available at `data/sample.jpg` (use in integration tests and for manual verification)

