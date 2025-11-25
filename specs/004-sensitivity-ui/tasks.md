# Tasks: Sensitivity Dropdown for K-Means Bins

**Input**: Design documents from `/specs/004-sensitivity-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm tooling and dependencies support the dropdown changes.

- [X] T001 Verify PySide6 + pytest-qt versions in `pyproject.toml` support QComboBox + GUI tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared building blocks required by all user stories.

- [X] T002 Create controller contract documenting bin-count API in `specs/004-sensitivity-ui/contracts/main-controller.md`
- [X] T003 Refactor `ColorReductionSettings` to `bin_count` semantics in `src/models/settings_model.py`
- [X] T004 [P] Update validation/unit coverage for bin_count in `tests/unit/test_settings_model.py`

⚠️ Complete Phase 2 before starting any user story work.

---

## Phase 3: User Story 1 – Configure K-Means Bins via Dropdown (Priority: P1) 🎯 MVP

**Goal**: Users select exact k-means bin counts via dropdown and see immediate color reduction (dropdown disabled during processing).
**Independent Test**: Launch app, load sample image, select each dropdown option (None, 4…256); ensure color reduction updates instantly and dropdown is disabled while processing.

### Implementation

- [X] T005 [P] [US1] Replace sensitivity slider/spinbox with QComboBox + disabled-state logic in `src/views/controls_panel.py`
- [X] T006 [P] [US1] Wire new `bin_count_changed` signal in `src/views/main_window.py` to controller slots
- [X] T007 [US1] Implement `update_bin_count(Optional[int])` + processing lock handling in `src/controllers/main_controller.py`
- [X] T008 [US1] Rename/remove legacy sensitivity wiring across `src/views/controls_panel.py` and `src/views/main_window.py` (clean up orphaned methods)
- [X] T009 [P] [US1] Refresh GUI tests for dropdown behavior/disabled state in `tests/gui/test_controls_panel.py`
- [X] T010 [P] [US1] Update controller unit tests for bin count flow in `tests/unit/test_main_controller.py`
- [X] T011 [US1] Exercise dropdown-driven processing in `tests/integration/test_controller.py`
- [X] T012 [P] [US1] Ensure operation-chaining continues to honor bin counts in `tests/integration/test_operation_chaining.py`

Checkpoint: User Story 1 independently delivers dropdown-driven color reduction and passes GUI/unit/integration tests.

---

## Phase 4: User Story 2 – Default Selection & Reset Behavior (Priority: P2)

**Goal**: Dropdown defaults to “None”, resets to “None” on each image load, and migration clears legacy sensitivity values.
**Independent Test**: Load image A, select 128, load image B → dropdown returns to “None”; restart app → dropdown still “None”; verify existing configs/migration don’t crash.

### Implementation

- [ ] T013 [US2] Reset color reduction state to `None` on image load + branch entry points in `src/controllers/main_controller.py`
- [ ] T014 [US2] Invoke `ControlsPanel.set_bin_count(None)` after image load events within `src/views/main_window.py`
- [ ] T015 [US2] Ensure migration path clears legacy sensitivity fields (e.g., settings persistence/operation history) in `src/controllers/main_controller.py`
- [ ] T016 [P] [US2] Expand integration coverage for reset/migration scenarios in `tests/integration/test_controller.py`
- [ ] T017 [P] [US2] Add GUI regression for default “None” display after load in `tests/gui/test_controls_panel.py`

Checkpoint: User Story 2 validated independently—new images always start at “None”, migration safe, tests pass.

---

## Phase 5: Polish & Cross-Cutting

**Purpose**: Documentation, validation, and cleanup.

- [ ] T018 [P] Document dropdown workflow + reset steps in `QUICKSTART_VALIDATION.md`
- [ ] T019 [P] Update feature artifacts (plan/spec/contracts) for final code references in `specs/004-sensitivity-ui/`
- [ ] T020 Run full test suite + lint/type checks (`pytest`, `ruff`, `mypy`) and capture results in `tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) → Foundational (Phase 2) → User Story phases → Polish
- User stories depend on Foundational completion; US2 also depends on US1 code structure for shared controller logic.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2. Independent once foundation ready.
- **US2 (P2)**: Depends on US1 dropdown implementation to exist (needs `set_bin_count` helpers).

### Parallel Opportunities

- Tasks T005 & T006 can proceed in parallel (different view files) once T003 completes.
- T009/T010/T012 GUI/unit/integration tests can run in parallel after controller changes merge.
- In Phase 4, T016 and T017 may run concurrently after controller reset logic (T013-T015) lands.
- Polish tasks T018–T020 marked [P] can run concurrently after story phases conclude.

---

## Implementation Strategy

1. Complete Setup + Foundational (T001–T004) to establish bin-count model + contracts.
2. Deliver MVP by finishing all User Story 1 tasks (T005–T012) and validating dropdown-driven processing.
3. Layer User Story 2 (T013–T017) for reset/migration behavior without regressing US1.
4. Finish with Polish tasks (T018–T020): docs, validation, and repo-wide quality gates.

MVP Scope = User Story 1 (dropdown selection + immediate color reduction). User Story 2 and Polish can follow once MVP is stable.

