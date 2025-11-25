# Research: Sensitivity Dropdown for K-Means Bins

**Feature**: 004-sensitivity-ui  
**Date**: 2025-01-27

## Overview

Research findings for replacing the sensitivity slider with a dropdown for k-means bin configuration. This feature involves UI component changes and settings model updates, but no new technologies or patterns.

## Technical Decisions

### Decision 1: Use QComboBox for Dropdown

**Decision**: Use PySide6's `QComboBox` widget to replace the slider/spinbox combination.

**Rationale**: 
- QComboBox is the standard Qt widget for dropdown selections
- Already available in PySide6 (no new dependencies)
- Provides built-in keyboard navigation and accessibility
- Supports disabled state (required for processing lock)
- Matches existing UI patterns in the application

**Alternatives Considered**:
- Custom dropdown widget: Rejected - unnecessary complexity, QComboBox meets all requirements
- QListWidget with custom styling: Rejected - overkill for simple selection, QComboBox is more appropriate

### Decision 2: Store Bin Count as Optional[int] in Settings Model

**Decision**: Change `ColorReductionSettings.sensitivity: float` to `bin_count: Optional[int]` where `None` represents disabled color reduction.

**Rationale**:
- Directly represents the k-means parameter (no conversion needed)
- `None` clearly indicates disabled state (no magic numbers)
- Type-safe: only valid values (4, 8, 16, 32, 64, 128, 256, None) can be set
- Eliminates float-to-int conversion logic

**Alternatives Considered**:
- Keep sensitivity float, convert in controller: Rejected - adds unnecessary conversion logic, less type-safe
- Use enum for bin counts: Considered but rejected - Optional[int] is simpler and more flexible for future changes

### Decision 3: Reset to None on Image Load

**Decision**: Dropdown resets to "None" (disabled) when a new image is loaded.

**Rationale**:
- Each image starts with a clean slate (no color reduction)
- Prevents accidental application of previous image's settings
- Matches user expectation: new image = fresh start
- Simplifies state management (no need to persist selection)

**Alternatives Considered**:
- Persist selection across images: Rejected per spec clarification - user wants reset behavior
- Remember last used value: Rejected - adds complexity, not required by spec

### Decision 4: Disable Dropdown During Processing

**Decision**: Disable the dropdown widget while image processing is in progress.

**Rationale**:
- Prevents race conditions (changing value mid-processing)
- Clear visual feedback that operation is in progress
- Standard UX pattern for async operations
- QComboBox supports `setEnabled(False)` natively

**Alternatives Considered**:
- Queue changes until processing completes: Rejected - adds complexity, disabling is simpler and clearer
- Allow changes but ignore during processing: Rejected - confusing UX, user might not realize change was ignored

## Integration Points

### Existing Code Dependencies

1. **ColorReducer.reduce_colors()**: Already supports `k: Optional[int]` parameter - no changes needed
2. **MainController.update_sensitivity()**: Needs refactoring to `update_bin_count()` accepting `Optional[int]`
3. **ControlsPanel**: Currently has `_sensitivity_slider` and `_sensitivity_spinbox` - replace with `_bin_count_dropdown: QComboBox`
4. **SettingsModel.ColorReductionSettings**: Change `sensitivity: float` to `bin_count: Optional[int]`

### Migration Strategy

- **Existing Settings**: All existing `sensitivity` float values reset to `None` (bin_count) per FR-007
- **No Backward Compatibility**: Old sensitivity slider interface is removed (out of scope per spec)
- **Test Updates**: All tests using `sensitivity` parameter need updates to use `bin_count`

## Implementation Notes

- QComboBox items: ["None", "4", "8", "16", "32", "64", "128", "256"]
- Map dropdown index/string to Optional[int]: "None" → None, others → int(value)
- Signal: `bin_count_changed = Signal(Optional[int])` replaces `sensitivity_changed = Signal(float)`
- Controller method: `update_bin_count(bin_count: Optional[int])` replaces `update_sensitivity(sensitivity: float)`

## No Additional Research Required

All technical decisions are straightforward and use existing patterns. No external research, libraries, or new technologies needed. Implementation follows established MVC architecture and PySide6 best practices.

