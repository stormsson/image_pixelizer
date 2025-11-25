# Data Model: Sensitivity Dropdown for K-Means Bins

**Feature**: 004-sensitivity-ui  
**Date**: 2025-01-27

## Overview

This feature modifies the `ColorReductionSettings` data model to replace the `sensitivity` float field with a `bin_count` integer field that directly represents k-means cluster counts.

## Entity Changes

### ColorReductionSettings

**Location**: `src/models/settings_model.py`

**Current Structure**:
```python
@dataclass
class ColorReductionSettings:
    sensitivity: float = 0.0  # 0.0-1.0, controls color reduction
    is_enabled: bool = False
```

**New Structure**:
```python
@dataclass
class ColorReductionSettings:
    bin_count: Optional[int] = None  # None, 4, 8, 16, 32, 64, 128, 256
    is_enabled: bool = False
```

### Field Changes

| Field | Old Type | New Type | Validation | Notes |
|-------|----------|----------|------------|-------|
| `sensitivity` | `float` | **REMOVED** | N/A | Replaced by `bin_count` |
| `bin_count` | N/A | `Optional[int]` | Must be one of: `None`, `4`, `8`, `16`, `32`, `64`, `128`, `256` | New field |

### Validation Rules

**bin_count Validation**:
- `None`: Disables color reduction (`is_enabled = False`)
- Valid integers: `4`, `8`, `16`, `32`, `64`, `128`, `256` (powers of 2 from 4 to 256)
- Any other value: `ValueError` raised in `__post_init__`

**is_enabled Auto-Setting**:
- Automatically set to `True` when `bin_count` is not `None`
- Automatically set to `False` when `bin_count` is `None`

### State Transitions

```
Initial State: bin_count = None, is_enabled = False
    ↓
User selects bin count (e.g., 16)
    ↓
State: bin_count = 16, is_enabled = True
    ↓
User selects "None"
    ↓
State: bin_count = None, is_enabled = False
```

### Relationships

- **ColorReductionSettings** → **ColorReducer**: `bin_count` passed directly as `k` parameter to `reduce_colors(image, sensitivity=0.0, k=bin_count)`
- **ColorReductionSettings** → **SettingsModel**: Part of `SettingsModel.color_reduction` attribute
- **SettingsModel** → **MainController**: Controller reads/writes `bin_count` from settings model

## Migration

### Existing Data

- **Current**: All `ColorReductionSettings` instances have `sensitivity: float` (0.0-1.0)
- **Migration**: All existing `sensitivity` values reset to `None` (bin_count)
- **Rationale**: Per FR-007, migration strategy is reset to default rather than conversion

### Code Impact

**Files Requiring Updates**:
1. `src/models/settings_model.py`: Change field definition and validation
2. `src/controllers/main_controller.py`: Update references from `sensitivity` to `bin_count`
3. `src/views/controls_panel.py`: Update UI to use dropdown instead of slider
4. All test files referencing `sensitivity`: Update to use `bin_count`

## Validation Example

```python
# Valid
settings = ColorReductionSettings(bin_count=16)  # is_enabled = True
settings = ColorReductionSettings(bin_count=None)  # is_enabled = False

# Invalid - raises ValueError
settings = ColorReductionSettings(bin_count=10)  # Not a power of 2
settings = ColorReductionSettings(bin_count=512)  # Exceeds 256
```

## No Additional Entities

No new entities are created. Only modification to existing `ColorReductionSettings` dataclass.

