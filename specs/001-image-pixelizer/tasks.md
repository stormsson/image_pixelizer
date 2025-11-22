# Tasks: Image Pixelizer Application

**Input**: Design documents from `/specs/001-image-pixelizer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per FR-019 through FR-022. Each meaningful entity and feature must have pytest tests. Unit tests for models and services, pytest-qt tests for GUI components, and integration tests for end-to-end workflows. Coverage targets: 80% for business logic, 60% for UI components.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (src/models/, src/services/, src/views/, src/controllers/, tests/)
- [x] T002 Initialize Python project with PySide6, Pillow, NumPy dependencies in requirements.txt or pyproject.toml
- [x] T003 [P] Configure linting (ruff) and formatting (black) tools
- [x] T004 [P] Configure type checking (mypy) in pyproject.toml
- [x] T005 [P] Setup pytest and pytest-qt for testing framework

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create base error handling infrastructure in src/services/__init__.py
- [x] T007 [P] Create ImageModel class in src/models/image_model.py with width, height, pixel_data, original_pixel_data, format, has_alpha attributes
- [x] T008 [P] Create SettingsModel class in src/models/settings_model.py with PixelizationSettings and ColorReductionSettings
- [x] T009 [P] Create ImageStatistics class in src/models/image_model.py with distinct_color_count, width, height, hover_hex_color attributes
- [x] T010 Create MainController base structure in src/controllers/main_controller.py with signal definitions

### Tests for Foundational Components

> **NOTE: Write these tests to verify models work correctly before proceeding**

- [x] T066 [P] Write unit tests for ImageModel in tests/unit/test_image_model.py (validation, dimensions, pixel_data, original_pixel_data, format, has_alpha)
- [x] T067 [P] Write unit tests for ImageStatistics in tests/unit/test_image_model.py (distinct_color_count, width, height, hover_hex_color validation, HEX format validation)
- [x] T068 [P] Write unit tests for SettingsModel in tests/unit/test_settings_model.py (PixelizationSettings, ColorReductionSettings, validation rules, ranges)
- [x] T069 [P] Write unit tests for rgb_to_hex utility function in tests/unit/test_image_model.py (RGB to HEX conversion, alpha channel support)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and Display Image (Priority: P1) 🎯 MVP

**Goal**: Users can load image files and see them displayed in the main content area with status bar showing dimensions

**Independent Test**: Open application, load an image file, verify image appears in main content area with correct dimensions and visual quality. Status bar should display image dimensions.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T070 [P] [US1] Write unit tests for ImageLoader service in tests/unit/test_image_loader.py (load_image, validate_image_format, validate_image_size, error handling)
- [x] T071 [P] [US1] Write pytest-qt tests for MainWindow in tests/gui/test_main_window.py (menu actions, file dialog, signal connections, error display)
- [x] T072 [P] [US1] Write pytest-qt tests for ImageView in tests/gui/test_image_view.py (image display, scaling, aspect ratio preservation)
- [x] T073 [P] [US1] Write pytest-qt tests for StatusBar in tests/gui/test_status_bar.py (statistics display, dimension formatting)
- [x] T074 [US1] Write integration test for load image workflow in tests/integration/test_image_processing.py (end-to-end: file dialog → load → display → status bar update)

### Implementation for User Story 1

- [x] T011 [US1] Implement ImageLoader service in src/services/image_loader.py with load_image, validate_image_format, validate_image_size methods
- [x] T012 [US1] Implement image loading error handling with user-friendly messages in src/services/image_loader.py
- [x] T013 [US1] Create MainWindow view in src/views/main_window.py with QMainWindow structure, menu bar, and basic layout
- [x] T014 [US1] Create ImageView widget in src/views/image_view.py for displaying images in main content area with QLabel and QPixmap
- [x] T015 [US1] Create StatusBar widget in src/views/status_bar.py for displaying image statistics at bottom of window
- [x] T016 [US1] Implement load_image method in src/controllers/main_controller.py to coordinate ImageLoader, update ImageModel, and emit signals
- [x] T017 [US1] Connect file dialog (QFileDialog) to load action in src/views/main_window.py
- [x] T018 [US1] Implement image display logic in src/views/image_view.py to show loaded image scaled to fit while maintaining aspect ratio
- [x] T019 [US1] Implement status bar update logic in src/views/status_bar.py to display image dimensions from ImageStatistics
- [x] T020 [US1] Connect controller signals to view updates in src/views/main_window.py (image_loaded, statistics_updated signals)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - users can load images and see them displayed

---

## Phase 4: User Story 2 - Pixelize Image with Adjustable Size (Priority: P2)

**Goal**: Users can adjust pixel size slider to apply pixelization effects that update in real-time

**Independent Test**: Load an image, adjust pixel size slider, verify image updates to show larger or smaller pixel blocks based on slider position. Effect should be visually apparent and update smoothly.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T075 [P] [US2] Write unit tests for Pixelizer service in tests/unit/test_pixelizer.py (pixelize method, block averaging algorithm, edge cases, pixel_size=1, large blocks)
- [x] T076 [P] [US2] Write pytest-qt tests for ControlsPanel in tests/gui/test_controls_panel.py (pixel size slider, range validation, signal emissions)
- [x] T077 [US2] Write integration test for pixelization workflow in tests/integration/test_image_processing.py (load → pixelize → verify effect)

### Implementation for User Story 2

- [x] T021 [US2] Implement Pixelizer service in src/services/pixelizer.py with pixelize method using block averaging algorithm
- [x] T022 [US2] Implement pixelization algorithm with NumPy operations for efficient block processing in src/services/pixelizer.py
- [x] T023 [US2] Create ControlsPanel widget in src/views/controls_panel.py with QSlider for pixel size control
- [x] T024 [US2] Implement pixel size slider with appropriate range (1-50) in src/views/controls_panel.py
- [x] T025 [US2] Implement update_pixel_size method in src/controllers/main_controller.py to process image and update model
- [x] T026 [US2] Connect pixel size slider signal to controller in src/views/controls_panel.py
- [x] T027 [US2] Implement real-time image update in src/views/image_view.py when pixelization is applied
- [ ] T028 [US2] Add threading support (QThread) for background pixelization processing in src/controllers/main_controller.py to maintain UI responsiveness (deferred - can be added later if performance issues occur)
- [x] T029 [US2] Update status bar to show processed image state in src/views/status_bar.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can load images and apply pixelization

---

## Phase 5: User Story 3 - Color Reduction with Sensitivity Control (Priority: P3)

**Goal**: Users can adjust sensitivity slider to reduce number of distinct colors, with status bar showing updated color count

**Independent Test**: Load and pixelize an image, adjust sensitivity slider, verify number of distinct colors changes (shown in status bar) and visual appearance reflects color reduction. Higher sensitivity should result in fewer colors.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T078 [P] [US3] Write unit tests for ColorReducer service in tests/unit/test_color_reducer.py (reduce_colors method, count_distinct_colors, sensitivity ranges, color quantization)
- [x] T079 [US3] Write integration test for color reduction workflow in tests/integration/test_image_processing.py (load → pixelize → reduce colors → verify color count)

### Implementation for User Story 3

- [x] T030 [US3] Implement ColorReducer service in src/services/color_reducer.py with reduce_colors method using threshold-based color quantization
- [x] T031 [US3] Implement color reduction algorithm with NumPy operations for efficient color distance calculations in src/services/color_reducer.py
- [x] T032 [US3] Implement count_distinct_colors method in src/services/color_reducer.py to compute unique color count
- [x] T033 [US3] Add sensitivity slider to ControlsPanel in src/views/controls_panel.py with appropriate range (0.0-1.0)
- [x] T034 [US3] Implement update_sensitivity method in src/controllers/main_controller.py to process image and update model
- [x] T035 [US3] Connect sensitivity slider signal to controller in src/views/controls_panel.py
- [x] T036 [US3] Implement real-time image update in src/views/image_view.py when color reduction is applied
- [x] T037 [US3] Update status bar to show distinct color count in src/views/status_bar.py
- [x] T038 [US3] Ensure color reduction is applied after pixelization in processing order in src/controllers/main_controller.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can load, pixelize, and reduce colors

---

## Phase 6: User Story 4 - Status Bar Information Display with Mouse Hover (Priority: P4)

**Goal**: Status bar displays image statistics and HEX color codes when mouse hovers over pixels, reverting to normal stats when mouse leaves

**Independent Test**: Load an image, verify status bar shows dimensions and color count. Hover over pixels and verify HEX color is displayed. Move mouse away and verify status bar reverts to normal statistics.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T080 [P] [US4] Write pytest-qt tests for mouse hover tracking in tests/gui/test_image_view.py (mouseMoveEvent, pixel color extraction, coordinate transformation)
- [x] T081 [P] [US4] Write pytest-qt tests for HEX color display in tests/gui/test_status_bar.py (hover_hex_color display, revert to normal stats on leaveEvent)
- [x] T082 [US4] Write integration test for mouse hover workflow in tests/integration/test_image_processing.py (load → hover → verify HEX → leave → verify revert)

### Implementation for User Story 4

- [x] T039 [US4] Implement mouse hover tracking in src/views/image_view.py using mouseMoveEvent to detect mouse position over image
- [x] T040 [US4] Implement pixel color extraction from ImageModel.pixel_data at mouse coordinates in src/views/image_view.py
- [x] T041 [US4] Implement RGB to HEX color conversion utility function in src/models/image_model.py or src/services/__init__.py
- [x] T042 [US4] Implement update_hover_color method in src/controllers/main_controller.py to extract color and update ImageStatistics
- [x] T043 [US4] Implement clear_hover_color method in src/controllers/main_controller.py to reset hover_hex_color when mouse leaves
- [x] T044 [US4] Connect mouse hover events from ImageView to controller in src/views/image_view.py
- [x] T045 [US4] Implement leaveEvent handler in src/views/image_view.py to detect when mouse leaves image area
- [x] T046 [US4] Update status bar display logic in src/views/status_bar.py to show HEX color when hover_hex_color is set, otherwise show normal statistics
- [x] T047 [US4] Connect hover_color_changed signal from controller to status bar update in src/views/main_window.py

**Checkpoint**: At this point, User Stories 1-4 should all work independently - users can load, pixelize, reduce colors, and see HEX colors on hover

---

## Phase 7: User Story 5 - Save Pixelized Image (Priority: P5)

**Goal**: Users can save processed images as PNG files to preserve their work

**Independent Test**: Load an image, apply pixelization and color reduction, save the result. Verify saved PNG file can be opened in other applications and matches the displayed result.

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T083 [P] [US5] Write unit tests for ImageSaver service in tests/unit/test_image_saver.py (save_image method, PNG format, alpha channel preservation, error handling)
- [x] T084 [US5] Write integration test for save workflow in tests/integration/test_image_processing.py (load → process → save → verify PNG file)

### Implementation for User Story 5

- [x] T048 [US5] Implement ImageSaver service in src/services/image_saver.py with save_image method to convert NumPy array to PIL Image and save as PNG
- [x] T049 [US5] Implement PNG saving with alpha channel preservation in src/services/image_saver.py
- [x] T050 [US5] Implement save error handling with user-friendly messages in src/services/image_saver.py
- [x] T051 [US5] Add Save menu item and keyboard shortcut (Ctrl+S/Cmd+S) in src/views/main_window.py
- [x] T052 [US5] Implement file save dialog (QFileDialog) for PNG file selection in src/views/main_window.py
- [x] T053 [US5] Implement save_image method in src/controllers/main_controller.py to coordinate ImageSaver and emit save_completed signal
- [x] T054 [US5] Connect save action to controller in src/views/main_window.py
- [x] T055 [US5] Implement save validation to check if image is loaded before allowing save in src/controllers/main_controller.py
- [x] T056 [US5] Implement save confirmation message to user after successful save in src/views/main_window.py
- [x] T057 [US5] Handle save errors (permissions, disk full) with clear error messages in src/controllers/main_controller.py
- [x] T088 [US5] Add SAVE button in src/views/controls_panel.py with save_requested signal
- [x] T089 [US5] Implement button visibility control in src/views/controls_panel.py (visible only when image is loaded, hidden when no image)
- [x] T090 [US5] Add set_image_loaded method in src/views/controls_panel.py to update button visibility based on image state
- [x] T091 [US5] Connect controls panel save button signal to controller save method in src/views/main_window.py
- [x] T092 [US5] Update main window to call set_image_loaded on controls panel when image_loaded/image_updated signals are received

### Tests for Controls Panel Save Button

- [x] T093 [P] [US5] Write GUI test for save button visibility in tests/gui/test_controls_panel.py (hidden initially, visible after image load, hidden after image cleared)

**Checkpoint**: At this point, all user stories should be complete - users can load, pixelize, reduce colors, see HEX colors, and save results

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T058 [P] Add docstrings to all public APIs (services, models, controller) following Google style
- [x] T059 [P] Add type hints throughout codebase (NumPy arrays, PIL Images, Qt types)
- [x] T060 Code cleanup and refactoring to ensure PEP 8 compliance
- [x] T061 [P] Performance optimization for image processing (caching, efficient NumPy operations)
- [x] T062 [P] Improve error messages across all user-facing operations
- [x] T063 [P] Add keyboard shortcuts documentation and accessibility improvements
- [x] T064 Validate all edge cases from spec.md are handled (large images, corrupted files, etc.)
- [x] T065 Run quickstart.md validation to ensure user workflow matches implementation
- [x] T085 [P] Write integration test for MainController in tests/integration/test_controller.py (signal/slot connections, error propagation, state management)
- [x] T086 [P] Verify test coverage meets targets (80% business logic, 60% UI) using pytest-cov
- [x] T087 [P] Add test fixtures and helpers in tests/conftest.py for common test setup (sample images, mock controllers, etc.)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 (needs image loaded)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US2 (applies color reduction after pixelization)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1 (needs image to hover over)
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Depends on US1 (needs image to save)

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation (TDD approach)
- Models before services
- Services before views/controllers
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T007, T008, T009)
- Once Foundational phase completes:
  - US1, US2, US3, US4, US5 can be worked on in parallel by different developers (with coordination)
  - Within each story, tasks marked [P] can run in parallel
- Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Models can be created in parallel:
Task: "Create ImageModel class in src/models/image_model.py"
Task: "Create SettingsModel class in src/models/settings_model.py"
Task: "Create ImageStatistics class in src/models/image_model.py"

# Views can be created in parallel:
Task: "Create MainWindow view in src/views/main_window.py"
Task: "Create ImageView widget in src/views/image_view.py"
Task: "Create StatusBar widget in src/views/status_bar.py"
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
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (load/display)
   - Developer B: User Story 2 (pixelization) - can start after US1 models ready
   - Developer C: User Story 4 (status bar/hover) - can start after US1 models ready
3. After US1-2 complete:
   - Developer A: User Story 3 (color reduction)
   - Developer B: User Story 5 (save)
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
- Mouse hover tracking requires coordinate transformation (screen to image coordinates)
- Save functionality must preserve alpha channel for PNG format
- Real-time updates require efficient NumPy operations and threading for responsiveness

