# Tasks: Alternative Background Removal Method

**Input**: Design documents from `/specs/003-alternative-background-removal/`
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

- [X] T001 Add openai>=1.0.0 dependency to requirements.txt with pinned version
- [ ] T002 [P] Create .env.sample file in project root with OPENAI_API_KEY template
- [X] T003 [P] Update .gitignore to ensure .env is ignored (verify it's already there)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create OpenAIBackgroundRemovalError exception class in src/services/__init__.py with user_message and technical_message attributes
- [X] T005 [P] Create OpenAIBackgroundRemover service class skeleton in src/services/openai_background_remover.py with __init__ method that loads API key from environment

### Tests for Foundational Components

> **NOTE: Write these tests to verify models work correctly before proceeding**

- [X] T050 [P] Write unit tests for OpenAIBackgroundRemovalError in tests/unit/test_openai_background_remover.py (exception creation, user_message attribute, technical_message attribute)
- [X] T051 [P] Write unit tests for API key loading in tests/unit/test_openai_background_remover.py (load from env var, load from parameter, missing key error, invalid key format error)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Automatic Background Removal (Priority: P1) 🎯 MVP

**Goal**: Users can click "Remove Background (Automatic)" button to automatically remove backgrounds without point selection. The application processes the image using OpenAI Vision API, making the background transparent while preserving the main subject. The operation completes automatically within 5 seconds for typical images.

**Independent Test**: Load an image, click "Remove Background (Automatic)" button, verify that the background becomes transparent (or is removed) while the foreground subject remains visible. The operation should complete automatically without requiring user interaction, and the result should be visually apparent within 5 seconds.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T052 [P] [US1] Write unit tests for image input format conversion in tests/unit/test_openai_background_remover.py (file path → PIL, bytes → PIL, PIL Image → PIL, NumPy array → PIL, invalid formats)
- [X] T053 [P] [US1] Write unit tests for image validation in tests/unit/test_openai_background_remover.py (dimension limits 2000x2000px, format validation, corrupted image handling)
- [X] T054 [P] [US1] Write unit tests for base64 encoding in tests/unit/test_openai_background_remover.py (PIL Image → base64, format preservation)
- [X] T055 [P] [US1] Write unit tests for API request construction in tests/unit/test_openai_background_remover.py (prompt text, image encoding, model selection, request format)
- [X] T056 [P] [US1] Write unit tests for API response parsing in tests/unit/test_openai_background_remover.py (text response parsing, foreground/background extraction, mask creation)
- [X] T057 [P] [US1] Write unit tests for error handling in tests/unit/test_openai_background_remover.py (network errors, rate limits, API errors, invalid responses - all with mocked API)
- [X] T058 [P] [US1] Write unit tests for optional file saving in tests/unit/test_openai_background_remover.py (save_path provided saves file, no save_path returns image data)
- [X] T059 [P] [US1] Write unit tests for output format handling in tests/unit/test_openai_background_remover.py (ImageModel return for app integration, PIL Image return for autonomous use, bytes return)
- [X] T060 [US1] Write integration test for end-to-end workflow in tests/integration/test_openai_integration.py (load image → remove background → verify result, use mocked API, use data/sample.jpg)
- [X] T061 [P] [US1] Write pytest-qt tests for Remove Background (Automatic) button in tests/gui/test_controls_panel.py (button visibility, enabled/disabled states, signal emissions, button labeling)
- [X] T062 [P] [US1] Write pytest-qt tests for UI disable/enable during automatic background removal in tests/gui/test_main_window.py (UI disabled when processing starts, UI enabled when processing completes, all controls disabled during processing)

### Implementation for User Story 1

#### OpenAIBackgroundRemover Service Implementation

- [X] T006 [US1] Implement image input format detection and conversion in src/services/openai_background_remover.py (support str, Path, bytes, PIL.Image.Image, np.ndarray → convert all to PIL Image)
- [X] T007 [US1] Implement image validation in src/services/openai_background_remover.py (check dimensions <= 2000x2000px, validate format, handle corrupted images)
- [X] T008 [US1] Implement base64 image encoding in src/services/openai_background_remover.py (convert PIL Image to base64-encoded PNG/JPEG for API)
- [X] T009 [US1] Implement OpenAI client initialization in src/services/openai_background_remover.py (lazy initialization, API key validation, client creation)
- [X] T010 [US1] Implement API request construction in src/services/openai_background_remover.py (build chat.completions.create request with prompt "remove the background from the attached file" and base64 image)
- [X] T011 [US1] Implement API call execution in src/services/openai_background_remover.py (call OpenAI Vision API with GPT-4 Vision model, handle timeouts, network errors)
- [X] T012 [US1] Implement API response parsing in src/services/openai_background_remover.py (extract text response, parse foreground/background information, create processing instructions)
- [X] T013 [US1] Implement local image processing in src/services/openai_background_remover.py (apply mask/instructions from API response to original image, create transparent background)
- [X] T014 [US1] Implement output format conversion in src/services/openai_background_remover.py (convert processed image to ImageModel, PIL Image, or bytes based on input type and save_path)
- [X] T015 [US1] Implement optional file saving in src/services/openai_background_remover.py (if save_path provided, save image to file and return ImageModel)
- [X] T016 [US1] Implement comprehensive error handling in src/services/openai_background_remover.py (API key errors, network errors, rate limits, API errors, processing errors - all with user-friendly messages)
- [X] T017 [US1] Implement remove_background method in src/services/openai_background_remover.py (main public API method that orchestrates all steps: input conversion → validation → API call → processing → output)

#### Controller Integration

- [X] T018 [US1] Add openai_background_remover attribute to MainController in src/controllers/main_controller.py (initialize OpenAIBackgroundRemover instance, load from environment)
- [X] T019 [US1] Create OpenAIBackgroundRemovalWorker class in src/controllers/main_controller.py (QObject worker for background processing, similar to BackgroundRemovalWorker)
- [X] T020 [US1] Implement remove_background_automatic method in src/controllers/main_controller.py (check image loaded, create worker and thread, connect signals, start processing)
- [X] T021 [US1] Implement _on_openai_background_removal_complete method in src/controllers/main_controller.py (handle successful processing, update image model, emit image_updated signal, add to operation history)
- [X] T022 [US1] Implement _on_openai_background_removal_error method in src/controllers/main_controller.py (handle errors, emit error_occurred signal with user-friendly message, restore UI state)
- [X] T023 [US1] Add openai_background_removal_thread and openai_background_removal_worker attributes to MainController in src/controllers/main_controller.py (track processing state)
- [X] T024 [US1] Update _on_thread_finished method in src/controllers/main_controller.py to handle OpenAI background removal thread cleanup
- [X] T025 [US1] Update operation history tracking in src/controllers/main_controller.py to include operation type (interactive vs automatic) when adding background removal operations

#### UI Integration - Controls Panel

- [X] T026 [US1] Add "Remove Background (Automatic)" button to ControlsPanel in src/views/controls_panel.py with openai_background_removal_requested signal
- [X] T027 [US1] Implement button visibility management in src/views/controls_panel.py (show when image loaded, hide when no image, same pattern as existing Remove Background button)
- [X] T028 [US1] Implement button enabled/disabled state in src/views/controls_panel.py (disabled when no image loaded, disabled during processing)
- [X] T029 [US1] Add button labeling and tooltip in src/views/controls_panel.py (clear label "Remove Background (Automatic)", tooltip explaining automatic vs interactive method)
- [X] T030 [US1] Implement _on_openai_remove_background_clicked handler in src/views/controls_panel.py (emit openai_background_removal_requested signal)
- [X] T031 [US1] Update button layout in src/views/controls_panel.py to place automatic button near interactive button with clear visual distinction

#### UI Integration - Point Selection Mode Handling

- [X] T032 [US1] Implement exit point selection mode logic in src/controllers/main_controller.py (when automatic method clicked during point selection, exit point selection mode, discard points, start automatic processing)
- [X] T033 [US1] Update remove_background_automatic method in src/controllers/main_controller.py to check and exit point selection mode if active

#### Main Window Integration

- [X] T034 [US1] Connect openai_background_removal_requested signal from ControlsPanel to remove_background_automatic method in MainWindow in src/views/main_window.py
- [X] T035 [US1] Verify UI disable/enable signals are connected in src/views/main_window.py (processing_started and processing_finished signals from controller should disable/enable UI)

#### Main Application Integration

- [X] T036 [US1] Initialize OpenAIBackgroundRemover in main.py (create instance, pass to MainController constructor, handle initialization errors)
- [X] T037 [US1] Update MainController constructor in src/controllers/main_controller.py to accept openai_background_remover parameter (optional, can be None if API key not configured)

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, edge cases, and cross-cutting improvements

### Error Handling Improvements

- [ ] T038 [P] Add retry logic for transient network errors in src/services/openai_background_remover.py (exponential backoff, max retries)
- [X] T039 [P] Improve error messages for rate limit scenarios in src/services/openai_background_remover.py (suggest wait time, provide helpful guidance)

### Performance Optimizations

- [ ] T040 [P] Add image size optimization in src/services/openai_background_remover.py (resize very large images before API call if needed, balance quality vs API costs)
- [ ] T041 [P] Add caching for API responses in src/services/openai_background_remover.py (optional: cache results for identical images to reduce API calls)

### Documentation

- [X] T042 [P] Add comprehensive docstrings to OpenAIBackgroundRemover class in src/services/openai_background_remover.py (Google-style docstrings, examples, parameter descriptions)
- [X] T043 [P] Update README.md with OpenAI API setup instructions (how to get API key, configure .env file, usage examples)

### Edge Case Handling

- [ ] T044 [P] Handle images with existing transparency in src/services/openai_background_remover.py (process normally, potentially refine existing transparency)
- [ ] T045 [P] Handle multiple sequential applications in src/services/openai_background_remover.py (each application processes current state, not original)
- [ ] T046 [P] Add progress indication for large images in src/controllers/main_controller.py (optional: show progress during API call)

### Operation Chaining (FR-017) - Functional Requirement

**Purpose**: Ensure pixelization and color reduction operations work on the current image state (including background removal modifications), not the original loaded image.

- [X] T063 [US1] Update update_pixel_size method in src/controllers/main_controller.py to use current pixel_data instead of original_pixel_data (pixelization should work on current state including background removal)
- [X] T064 [US1] Update update_color_reduction_sensitivity method in src/controllers/main_controller.py to use current pixel_data instead of original_pixel_data (color reduction should work on current state including background removal)
- [X] T065 [US1] Verify undo operation correctly preserves and reapplies pixelization/color reduction on restored state in src/controllers/main_controller.py (ensure undo maintains operation chain: background removal → pixelization → color reduction)
- [X] T066 [P] [US1] Write unit test for operation chaining in tests/unit/test_main_controller.py (test that pixelization works on image with background removed, test that color reduction works on pixelized image with background removed)
- [X] T067 [P] [US1] Write integration test for operation chaining workflow in tests/integration/test_operation_chaining.py (load image → remove background → apply pixelization → apply color reduction → verify all operations chain correctly)

### Two-Step Color Reduction (FR-018 to FR-022) - Functional Requirement

**Purpose**: Implement two-step color reduction process: Step 1 (quantization) rounds colors to nearest multiples, Step 2 (global palette clustering) groups similar colors using distance threshold and replaces with weighted average. Step 2 runs after Step 1, with sensitivity controlling both steps.

#### Tests for Two-Step Color Reduction

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T068 [P] Write unit test for Step 2 (global palette clustering) color distance calculation in tests/unit/test_color_reducer.py (Euclidean distance in RGB space, distance threshold mapping from sensitivity, verify higher sensitivity = larger threshold)
- [X] T069 [P] Write unit test for Step 2 color grouping in tests/unit/test_color_reducer.py (group similar colors within threshold, verify groups are created correctly, test edge cases: no similar colors, all colors similar)
- [X] T070 [P] Write unit test for Step 2 weighted average calculation in tests/unit/test_color_reducer.py (weighted mean by pixel count, verify colors appearing more often have more influence, test with different color frequencies)
- [X] T071 [P] Write unit test for two-step pipeline execution in tests/unit/test_color_reducer.py (Step 1 runs first, Step 2 runs after Step 1 on quantized result, verify both steps use sensitivity parameter, test sensitivity=0.0 skips both steps)
- [X] T072 [P] Write unit test for Step 2 with alpha channel in tests/unit/test_color_reducer.py (preserve alpha channel during clustering, only cluster RGB channels, maintain transparency)
- [X] T073 [P] Write integration test for two-step color reduction workflow in tests/integration/test_color_reduction.py (load image → apply color reduction → verify Step 1 quantization applied → verify Step 2 clustering applied → verify final color count reduced)

#### Implementation for Two-Step Color Reduction

- [X] T074 Implement _calculate_distance_threshold method in src/services/color_reducer.py (map sensitivity 0.0-1.0 to distance threshold, higher sensitivity = larger threshold, use appropriate range for RGB space)
- [X] T075 Implement _calculate_color_distance method in src/services/color_reducer.py (Euclidean distance in RGB space, handle 3-channel RGB and 4-channel RGBA, return float distance value)
- [X] T076 Implement _identify_distinct_colors method in src/services/color_reducer.py (extract all unique colors from quantized image, count pixel frequency for each color, return color palette with frequencies)
- [X] T077 Implement _group_similar_colors method in src/services/color_reducer.py (group colors within distance threshold, use greedy clustering algorithm, return color groups with member colors and pixel counts)
- [X] T078 Implement _calculate_weighted_average_color method in src/services/color_reducer.py (calculate weighted mean by pixel count for each color group, handle RGB channels separately, return average color for each group)
- [X] T079 Implement _apply_palette_clustering method in src/services/color_reducer.py (orchestrate Step 2: identify distinct colors → group similar colors → calculate weighted averages → replace colors in image, preserve alpha channel)
- [X] T080 Update reduce_colors method in src/services/color_reducer.py to execute Step 2 after Step 1 (run quantization first, then pass quantized result to palette clustering, ensure both steps controlled by sensitivity)
- [X] T081 Update docstring for reduce_colors method in src/services/color_reducer.py (document two-step process, explain Step 1 quantization and Step 2 clustering, clarify sensitivity controls both steps, update parameter descriptions)

### Testing Coverage

- [ ] T047 [P] Add edge case tests in tests/unit/test_openai_background_remover.py (images with existing transparency, multiple sequential applications, very large images, similar subject/background colors)
- [ ] T048 [P] Add integration tests for error scenarios in tests/integration/test_openai_integration.py (network failures, rate limits, invalid API key, corrupted images)

---

## Dependencies

### User Story Completion Order

- **Phase 1 (Setup)**: Must complete before any other work
- **Phase 2 (Foundational)**: Must complete before Phase 3
- **Phase 3 (User Story 1)**: Can begin after Phase 2 complete
  - Service implementation (T006-T017) can be done in parallel with controller/UI work (T018-T037)
  - Tests (T052-T062) should be written before implementation (TDD approach)
- **Phase 4 (Polish)**: Can be done in parallel or after Phase 3 complete

### Parallel Execution Opportunities

**Within Phase 3 (User Story 1)**:
- Service implementation tasks (T006-T017) can be done in parallel groups:
  - T006-T008: Input handling (can be parallel)
  - T009-T012: API interaction (sequential within group)
  - T013-T017: Processing and output (sequential within group)
- Controller integration (T018-T025) can be done in parallel with UI integration (T026-T035)
- Tests (T052-T062) can be written in parallel groups

**Within Phase 4 (Polish)**:
- All tasks (T038-T048) can be done in parallel
- Two-step color reduction tasks (T068-T081):
  - Test tasks (T068-T073) can be written in parallel
  - Implementation tasks (T074-T081) can be done in parallel groups:
    - T074-T076: Helper methods (can be parallel)
    - T077-T079: Clustering logic (sequential within group)
    - T080-T081: Integration and documentation (sequential)

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP includes**: Phase 1, Phase 2, and Phase 3 (User Story 1) - Automatic background removal with OpenAI API integration.

**MVP delivers**:
- Working "Remove Background (Automatic)" button
- OpenAI API integration for automatic background removal
- UI integration with disable/enable during processing
- Error handling with user-friendly messages
- Operation history tracking
- Basic test coverage

**MVP excludes**: Phase 4 polish tasks (retry logic, caching, advanced edge cases) - these can be added incrementally.

### Incremental Delivery

1. **Setup & Foundation** (Phase 1-2): Environment configuration, exception class, service skeleton
2. **Core Service** (Phase 3, Service tasks): Complete OpenAIBackgroundRemover service with all input/output formats
3. **Integration** (Phase 3, Controller/UI tasks): Connect service to controller and UI
4. **Testing** (Phase 3, Test tasks): Comprehensive test coverage
5. **Polish** (Phase 4): Error handling improvements, performance optimizations, edge cases

### Testing Strategy

- **TDD Approach**: Write tests first (T052-T062), ensure they fail, then implement (T006-T037)
- **Unit Tests**: Test service class independently with mocked API
- **Integration Tests**: Test end-to-end workflow with mocked API
- **GUI Tests**: Test UI components with pytest-qt
- **Coverage Target**: 80% for business logic (service class), 60% for UI components

## Task Summary

- **Total Tasks**: 81 tasks
- **Setup Tasks**: 3 tasks (Phase 1)
- **Foundational Tasks**: 2 tasks + 2 test tasks (Phase 2)
- **User Story 1 Tasks**: 32 implementation tasks + 11 test tasks + 5 operation chaining tasks (Phase 3)
- **Polish Tasks**: 11 tasks + 14 two-step color reduction tasks (Phase 4)
- **Parallel Opportunities**: Multiple tasks can be executed in parallel within each phase

## Independent Test Criteria

### User Story 1 - Automatic Background Removal

**Test Scenario**: 
1. Load an image using existing "Load Image" button
2. Click "Remove Background (Automatic)" button
3. Wait for processing (UI should be disabled during processing)
4. Verify background becomes transparent while subject remains visible
5. Verify image dimensions preserved
6. Verify operation can be undone
7. Verify error handling works (test with invalid API key, network error)

**Success Criteria**:
- Background removal completes within 5 seconds for images up to 2000x2000px
- Background is transparent (alpha channel = 0 for background pixels)
- Main subject is preserved and visible
- Image dimensions match original
- Operation is tracked in undo history
- Error messages are user-friendly and actionable

