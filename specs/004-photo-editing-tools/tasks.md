# Tasks: Photographic Editing Tools

**Input**: Design documents from `/specs/004-photo-editing-tools/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per existing codebase standards. Each meaningful entity and feature must have pytest tests. Unit tests for services, pytest-qt tests for GUI components, and integration tests for end-to-end workflows. Coverage targets: 80% for business logic, 60% for UI components.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 [P] Verify no new dependencies needed (uses existing PySide6, NumPy, Pillow - all in requirements.txt)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Create LevelsAdjuster service class skeleton in src/services/levels_adjuster.py with class definition and placeholder methods

### Tests for Foundational Components

> **NOTE: Write these tests to verify service works correctly before proceeding**

- [X] T050 [P] Write unit tests for LevelsAdjuster class structure in tests/unit/test_levels_adjuster.py (class instantiation, method signatures)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Image Levels Tool (Priority: P1) 🎯 MVP

**Goal**: Users can access "Image Levels" from the main menu to open a tool window displaying a histogram and two sliders. Adjusting the sliders applies levels adjustment to the image in real-time, clipping highlights and shadows based on the slider values. The histogram updates to reflect changes, and the main image view updates immediately.

**Independent Test**: Load an image, access "Image Levels" from the main menu, verify histogram displays correctly, adjust both sliders, and confirm that the image updates to show the levels adjustment applied. The tool should work independently of other editing operations.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T051 [P] [US1] Write unit tests for histogram calculation in tests/unit/test_levels_adjuster.py (calculate histogram for test image, verify 256 bins, verify frequency counts, test with RGB image, test with RGBA image, test with uniform color, test with gradient)
- [X] T052 [P] [US1] Write unit tests for levels adjustment application in tests/unit/test_levels_adjuster.py (apply darks cutoff only, apply lights cutoff only, apply both cutoffs, verify pixel replacement, test with zero cutoffs, test with max cutoffs, preserve alpha channel)
- [X] T053 [P] [US1] Write unit tests for error handling in tests/unit/test_levels_adjuster.py (invalid image, invalid cutoff values, empty image, None image)
- [X] T054 [P] [US1] Write unit tests for histogram calculation edge cases in tests/unit/test_levels_adjuster.py (very dark image, very light image, single color image, grayscale image)
- [X] T055 [P] [US1] Write unit tests for levels adjustment edge cases in tests/unit/test_levels_adjuster.py (both sliders at 100%, overlapping thresholds, grayscale vs color images)
- [X] T056 [P] [US1] Write pytest-qt tests for LevelsWindow initialization in tests/gui/test_levels_window.py (window opens, title correct, histogram widget exists, sliders exist with correct ranges, window disabled when no image)
- [X] T057 [P] [US1] Write pytest-qt tests for histogram display in tests/gui/test_levels_window.py (histogram displays when image loaded, dark tones on left, light tones on right, bars proportional to frequency)
- [X] T058 [P] [US1] Write pytest-qt tests for slider functionality in tests/gui/test_levels_window.py (darks slider updates image, lights slider updates image, both sliders work together, slider values displayed correctly)
- [X] T059 [P] [US1] Write pytest-qt tests for real-time updates in tests/gui/test_levels_window.py (histogram updates on slider change, main view updates on slider change, no lag on rapid slider movement)
- [X] T060 [US1] Write integration test for end-to-end workflow in tests/integration/test_levels_integration.py (load image → open levels window → adjust sliders → verify image updated → verify operation history)

### Implementation for User Story 1

#### LevelsAdjuster Service Implementation

- [X] T003 [US1] Implement calculate_histogram method in src/services/levels_adjuster.py (convert RGB/RGBA to grayscale using luminance formula, use np.histogram with 256 bins, return frequency counts array)
- [X] T004 [US1] Implement apply_levels method in src/services/levels_adjuster.py (calculate percentile thresholds from histogram, create pixel mapping for darks and lights, apply mapping to RGB channels, preserve alpha channel, return new ImageModel)
- [X] T005 [US1] Implement input validation in src/services/levels_adjuster.py (validate ImageModel, validate cutoff values in range [0.0, 100.0], raise ValueError with clear messages)
- [X] T006 [US1] Add comprehensive docstrings to LevelsAdjuster class in src/services/levels_adjuster.py (Google-style docstrings, examples, parameter descriptions)

#### HistogramWidget Implementation

- [X] T007 [US1] Create HistogramWidget class in src/views/levels_window.py (QWidget subclass, paintEvent override, set_histogram_data method)
- [X] T008 [US1] Implement histogram drawing in HistogramWidget.paintEvent in src/views/levels_window.py (draw vertical bars, dark tones on left, light tones on right, normalize bar heights, use QPainter)
- [X] T009 [US1] Implement histogram data normalization in HistogramWidget in src/views/levels_window.py (normalize frequencies to 0.0-1.0 range, handle empty histogram, update display on data change)

#### LevelsWindow Implementation

- [X] T010 [US1] Create LevelsWindow class in src/views/levels_window.py (QMainWindow subclass, __init__ with controller parameter, setup UI components)
- [X] T011 [US1] Implement UI setup in LevelsWindow._setup_ui in src/views/levels_window.py (create histogram widget, create darks slider 0-100, create lights slider 0-100, create labels, layout widgets)
- [X] T012 [US1] Implement histogram calculation and display in LevelsWindow in src/views/levels_window.py (request image from controller, calculate histogram using LevelsAdjuster, display in HistogramWidget, cache histogram data)
- [X] T013 [US1] Implement slider value change handlers in LevelsWindow in src/views/levels_window.py (on_darks_slider_changed, on_lights_slider_changed, apply levels adjustment, emit levels_adjusted signal)
- [X] T014 [US1] Implement real-time updates in LevelsWindow in src/views/levels_window.py (update histogram on slider change, emit signal to controller, update main view)
- [X] T015 [US1] Implement image update handler in LevelsWindow in src/views/levels_window.py (on_image_updated slot, recalculate histogram when image changes, update display)
- [X] T016 [US1] Implement window state management in LevelsWindow in src/views/levels_window.py (disable sliders when no image, enable when image loaded, handle window close event)
- [X] T017 [US1] Add comprehensive docstrings to LevelsWindow class in src/views/levels_window.py (Google-style docstrings, signal/slot documentation)

#### Controller Integration

- [X] T018 [US1] Add levels_adjuster attribute to MainController in src/controllers/main_controller.py (initialize LevelsAdjuster instance)
- [X] T019 [US1] Implement apply_levels_adjustment method in src/controllers/main_controller.py (receive adjusted ImageModel from window, update image model, add to operation history, emit image_updated signal)
- [X] T020 [US1] Add get_current_image method to MainController in src/controllers/main_controller.py (return current ImageModel instance, return None if no image loaded)
- [X] T021 [US1] Update operation history tracking in src/controllers/main_controller.py to include levels adjustment operation type with parameters (darks_cutoff, lights_cutoff)

#### Main Window Integration

- [X] T022 [US1] Add "Photographic Editing Tools" menu to MainWindow in src/views/main_window.py (add menu to menu bar, add "Image Levels" submenu item)
- [X] T023 [US1] Implement menu item handler in MainWindow in src/views/main_window.py (_on_levels_menu_triggered method, check if image loaded, create LevelsWindow instance, show window)
- [X] T024 [US1] Implement menu item enable/disable logic in MainWindow in src/views/main_window.py (disable when no image loaded, enable when image loaded, connect to image_loaded signal)
- [X] T025 [US1] Connect levels_adjusted signal in MainWindow in src/views/main_window.py (connect LevelsWindow signal to controller method, handle window lifecycle)
- [X] T026 [US1] Implement window reference management in MainWindow in src/views/main_window.py (store LevelsWindow reference, prevent duplicate windows, handle window close)

#### Main Application Integration

- [X] T027 [US1] Initialize LevelsAdjuster in main.py (create instance, pass to MainController constructor)
- [X] T028 [US1] Update MainController constructor in src/controllers/main_controller.py to accept levels_adjuster parameter (optional, can be None for backward compatibility)

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, edge cases, and cross-cutting improvements

### Performance Optimizations

- [X] T029 [P] Add histogram caching in LevelsWindow in src/views/levels_window.py (cache histogram when image loads, only recalculate when image changes, not on every slider change)
- [X] T030 [P] Optimize levels adjustment for large images in src/services/levels_adjuster.py (use vectorized NumPy operations, minimize memory allocations, verify performance targets)

### Error Handling Improvements

- [X] T031 [P] Improve error messages for invalid inputs in src/services/levels_adjuster.py (specific error messages for each validation failure, user-friendly messages)
- [X] T032 [P] Add error handling for histogram calculation failures in src/views/levels_window.py (display error message, disable sliders, show user-friendly error)

### Documentation

- [X] T033 [P] Add usage examples to README.md (how to access Image Levels tool, basic usage examples)
- [X] T034 [P] Update architecture documentation with levels adjustment workflow

### Edge Case Handling

- [ ] T035 [P] Handle window close during adjustment in src/views/levels_window.py (ensure adjustments remain applied, cleanup resources)
- [ ] T036 [P] Handle rapid slider movements in src/views/levels_window.py (debounce or throttle if needed, ensure all updates processed)
- [ ] T037 [P] Handle multiple tool windows in src/views/main_window.py (allow multiple windows, each tracks its own state)

### Testing Coverage

- [ ] T038 [P] Add performance tests in tests/unit/test_levels_adjuster.py (verify histogram calculation < 500ms for 2000x2000px, verify levels adjustment < 100ms)
- [ ] T039 [P] Add edge case tests in tests/gui/test_levels_window.py (very large images, rapid slider movements, window lifecycle)

---

## Dependencies

### User Story Completion Order

- **Phase 1 (Setup)**: Must complete before any other work
- **Phase 2 (Foundational)**: Must complete before Phase 3
- **Phase 3 (User Story 1)**: Can begin after Phase 2 complete
  - Service implementation (T003-T006) can be done in parallel with widget/window work (T007-T017)
  - Tests (T051-T060) should be written before implementation (TDD approach)
- **Phase 4 (Polish)**: Can be done in parallel or after Phase 3 complete

### Parallel Execution Opportunities

**Within Phase 3 (User Story 1)**:
- Service implementation tasks (T003-T006) can be done in parallel groups:
  - T003-T004: Core methods (sequential within group)
  - T005-T006: Validation and documentation (can be parallel)
- Widget/Window implementation (T007-T017) can be done in parallel groups:
  - T007-T009: HistogramWidget (sequential within group)
  - T010-T017: LevelsWindow (sequential within group, but can start after T007-T009)
- Controller integration (T018-T021) can be done in parallel with window integration (T022-T026)
- Tests (T051-T060) can be written in parallel groups

**Within Phase 4 (Polish)**:
- All tasks (T029-T039) can be done in parallel

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP includes**: Phase 1, Phase 2, and Phase 3 (User Story 1) - Image Levels tool with histogram display and real-time adjustment.

**MVP delivers**:
- Working "Image Levels" menu item
- Tool window with histogram and sliders
- Real-time levels adjustment
- Integration with operation history
- Basic test coverage

**MVP excludes**: Phase 4 polish tasks (performance optimizations, advanced error handling) - these can be added incrementally.

### Incremental Delivery

1. **Setup & Foundation** (Phase 1-2): Verify dependencies, create service skeleton
2. **Core Service** (Phase 3, Service tasks): Complete LevelsAdjuster service with histogram and adjustment
3. **UI Components** (Phase 3, Widget/Window tasks): Complete HistogramWidget and LevelsWindow
4. **Integration** (Phase 3, Controller/Menu tasks): Connect service to controller and menu
5. **Testing** (Phase 3, Test tasks): Comprehensive test coverage
6. **Polish** (Phase 4): Performance optimizations, error handling improvements, edge cases

### Testing Strategy

- **TDD Approach**: Write tests first (T051-T060), ensure they fail, then implement (T003-T028)
- **Unit Tests**: Test service class independently
- **GUI Tests**: Test UI components with pytest-qt
- **Integration Tests**: Test end-to-end workflow
- **Coverage Target**: 80% for business logic (service class), 60% for UI components

## Phase 5: Fix Image Snapshot Reference (Critical Bug Fix)

**Purpose**: Fix the image snapshot capture behavior to ensure levels adjustments are always calculated against the snapshot captured when the window opens, not the live current state.

**Problem**: Current implementation recaptures the snapshot when `image_updated` signal is received, even when the update comes from our own levels adjustment. This breaks the requirement that all cutoff calculations must be against the snapshot at window open.

### Tests for Snapshot Behavior

> **NOTE: Write these tests FIRST to verify the bug and ensure the fix works**

- [X] T061 [P] [US1] Write unit test for snapshot capture on window open in tests/unit/test_levels_adjuster.py (verify snapshot is captured once when window opens, snapshot matches current image state at that moment)
- [X] T062 [P] [US1] Write unit test for snapshot persistence in tests/unit/test_levels_adjuster.py (verify snapshot does not change when levels adjustment is applied, verify snapshot does not change when image_updated signal is received from our own adjustment)
- [X] T063 [P] [US1] Write pytest-qt test for snapshot behavior in tests/gui/test_levels_window.py (open window → verify snapshot captured → apply levels → verify snapshot unchanged → receive image_updated → verify snapshot still unchanged)
- [X] T064 [P] [US1] Write integration test for snapshot behavior in tests/integration/test_levels_integration.py (open window → apply levels → verify adjustment based on snapshot → apply other operation → verify snapshot still based on original state)
- [X] T065 [P] [US1] Write test for snapshot recapture on new image in tests/gui/test_levels_window.py (open window with image A → load new image B → verify snapshot recaptured to image B state)

### Implementation for Snapshot Fix

- [X] T066 [US1] Fix snapshot capture logic in src/views/levels_window.py (capture snapshot only once when window opens, add flag to track if snapshot is already captured, prevent recapture in _on_image_updated when update comes from our own adjustment)
- [X] T067 [US1] Add snapshot capture flag in src/views/levels_window.py (add _snapshot_captured boolean flag, set to True after first capture, check flag before recapturing)
- [X] T068 [US1] Fix _on_image_updated handler in src/views/levels_window.py (do not recapture snapshot when image_updated signal is received from our own levels adjustment, only recapture if a truly new image is loaded)
- [X] T069 [US1] Implement proper image change detection in src/views/levels_window.py (use image reference or hash comparison to detect if image actually changed vs just pixel data modified, distinguish between new image load vs our own adjustment)
- [X] T070 [US1] Reset snapshot on window close/reopen in src/views/levels_window.py (ensure snapshot is reset when window is closed and reopened, capture fresh snapshot each time window opens)

## Task Summary

- **Total Tasks**: 70 tasks
- **Setup Tasks**: 1 task (Phase 1)
- **Foundational Tasks**: 1 task + 1 test task (Phase 2)
- **User Story 1 Tasks**: 26 implementation tasks + 10 test tasks (Phase 3)
- **Polish Tasks**: 11 tasks (Phase 4)
- **Snapshot Fix Tasks**: 5 test tasks + 5 implementation tasks (Phase 5)
- **Parallel Opportunities**: Multiple tasks can be executed in parallel within each phase

## Independent Test Criteria

### User Story 1 - Image Levels Tool

**Test Scenario**: 
1. Load an image using existing "Load Image" button
2. Select "Photographic Editing Tools > Image Levels" from menu
3. Verify histogram displays correctly (dark tones left, light tones right)
4. Adjust Darks Cutoff slider to 5%
5. Adjust Lights Cutoff slider to 10%
6. Verify image updates in real-time
7. Verify histogram updates to reflect changes
8. Close window and verify adjustments remain applied
9. Verify operation can be undone

**Success Criteria**:
- Tool window opens within 1 second (per spec SC-001)
- Histogram displays within 2 seconds for 2000x2000px images (per spec SC-002)
- Slider adjustments update display within 100ms (per spec SC-003)
- Both sliders work independently and together correctly
- Levels adjustments are tracked in operation history
- Undo functionality works correctly

