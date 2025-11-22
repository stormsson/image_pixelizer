# Data Model: Image Operations Feature

**Feature**: Image Operations in Controls Panel  
**Date**: 2025-01-27  
**Phase**: 1 - Design & Contracts

## Entities

### PointSelection

Represents a single point selected by the user on the image during background removal point selection mode.

**Attributes**:
- `x: int` - X coordinate of the point in image pixel space (0 to image width)
- `y: int` - Y coordinate of the point in image pixel space (0 to image height)
- `label: str` - Label indicating whether point is "keep" (foreground) or "remove" (background)

**Relationships**:
- Part of `PointSelectionCollection` (managed by controller during point selection mode)
- References image coordinates in `ImageModel` coordinate space

**Validation Rules**:
- `x` must be >= 0 and < image width
- `y` must be >= 0 and < image height
- `label` must be either "keep" or "remove"

**Lifecycle**:
1. Created when user clicks on image during point selection mode (left-click = keep, right-click = remove)
2. Stored in controller's point selection collection
3. Removed when:
   - User clicks "Cancel" (all points cleared)
   - User clicks "Apply" and background removal completes (points cleared after processing)
   - New image is loaded (all points cleared)
   - Point selection mode exits

**State Transitions**:
- `Created` → `Stored` (immediately after user click)
- `Stored` → `Removed` (when cleared or operation completes)

### PointSelectionCollection

Represents the collection of points selected during point selection mode.

**Attributes**:
- `points: List[PointSelection]` - List of selected points with their coordinates and labels
- `is_active: bool` - Whether point selection mode is currently active

**Operations**:
- `add_point(x: int, y: int, label: str)` - Add new point to collection
- `remove_point(x: int, y: int)` - Remove point at specific coordinates (if exists)
- `clear()` - Remove all points
- `get_keep_points() -> List[PointSelection]` - Get all points labeled "keep"
- `get_remove_points() -> List[PointSelection]` - Get all points labeled "remove"
- `get_count() -> int` - Get total number of points
- `to_sam_prompts() -> List[Dict[str, Any]]` - Convert points to SAM prompt format for rembg

**Validation Rules**:
- Points must have valid coordinates within image bounds
- Points must have valid labels ("keep" or "remove")

**Lifecycle**:
1. Created when "Remove Background" button is clicked (enters point selection mode)
2. Points added as user clicks on image
3. Cleared when "Cancel" is clicked or "Apply" completes
4. Destroyed when point selection mode exits

### OperationHistoryEntry

Represents a single entry in the operation history for undo functionality.

**Attributes**:
- `operation_type: str` - Type of operation that was applied (e.g., "remove_background"). Used to identify which operation to undo.
- `image_state: ImageModel` - Snapshot of the image state before the operation was applied. Contains full pixel data, dimensions, format, and transparency information.
- `timestamp: float` - Optional timestamp when the operation was recorded (for debugging/logging purposes). Uses `time.time()` format.

**Relationships**:
- Part of `OperationHistory` collection (managed by `OperationHistoryManager`)
- References `ImageModel` (existing entity)

**Validation Rules**:
- `operation_type` must not be empty
- `image_state` must be a valid `ImageModel` instance
- `timestamp` must be a positive float (if provided)

**Lifecycle**:
1. Created when a complex button-based operation is applied (e.g., "Remove Background")
2. Stored in `OperationHistoryManager` history list
3. Removed when:
   - History limit (20) is reached and this is the oldest entry (rolling history)
   - New image is loaded (all history cleared)
   - User explicitly clears history (future enhancement)

**State Transitions**:
- `Created` → `Stored` (immediately after creation)
- `Stored` → `Removed` (when history limit reached or image reloaded)

### OperationHistory (Collection)

Represents the complete operation history for the current image session.

**Attributes**:
- `entries: List[OperationHistoryEntry]` - Ordered list of operation history entries (most recent last)
- `max_size: int` - Maximum number of entries (fixed at 20 per spec)

**Operations**:
- `add_entry(entry: OperationHistoryEntry)` - Add new entry, remove oldest if limit reached
- `get_last_entry() -> Optional[OperationHistoryEntry]` - Get most recent entry for undo
- `remove_last_entry() -> Optional[OperationHistoryEntry]` - Remove and return most recent entry (for undo)
- `clear()` - Remove all entries (when new image loaded)
- `can_undo() -> bool` - Check if undo is available (history not empty)
- `get_count() -> int` - Get current number of entries

**Validation Rules**:
- Maximum 20 entries (enforced by `max_size`)
- Entries must be in chronological order (most recent last)

**Lifecycle**:
1. Created when application starts or new image is loaded
2. Entries added as operations are applied
3. Cleared when new image is loaded
4. Destroyed when application closes (in-memory only, no persistence)

## Integration with Existing Entities

### ImageModel (Existing - No Changes)

The existing `ImageModel` entity is used as the `image_state` attribute in `OperationHistoryEntry`. No modifications needed to `ImageModel` itself.

### SettingsModel (Existing - No Changes)

The existing `SettingsModel` (pixelization and color reduction settings) is NOT stored in operation history. Slider-based changes are preserved separately and reapplied after undo operations.

## Data Flow

### Point Selection and Background Removal Flow

1. User clicks "Remove Background" button
2. Controller enters point selection mode, creates `PointSelectionCollection`
3. Controller emits signal to enable point selection in `ImageView`
4. User clicks points on image:
   - Left-click: Creates `PointSelection` with `label="keep"`, adds to collection
   - Right-click: Creates `PointSelection` with `label="remove"`, adds to collection
5. `ImageView` displays visual markers (green for keep, red for remove) at clicked coordinates
6. Controller enables "Apply" button when at least one point is selected
7. User clicks "Apply" button
8. Controller captures current `ImageModel` state
9. Controller creates `OperationHistoryEntry` with:
   - `operation_type = "remove_background"`
   - `image_state = current ImageModel snapshot`
   - `timestamp = current time`
10. Controller converts `PointSelectionCollection` to SAM prompts format
11. Controller applies background removal operation with prompts
12. Controller adds entry to `OperationHistoryManager`
13. Controller clears point selection collection and exits point selection mode
14. Controller emits `image_updated` signal
15. UI updates to show processed image (markers removed)

### Undo Flow

1. User clicks "Undo" button
2. Controller checks `OperationHistoryManager.can_undo()`
3. Controller retrieves last entry from history
4. Controller restores `image_state` from entry
5. Controller reapplies current slider settings (pixelization/color reduction) to restored image
6. Controller removes entry from history
7. Controller emits `image_updated` signal
8. UI updates to show restored image

### History Management Flow

1. When adding 21st entry:
   - Remove oldest entry (index 0)
   - Add new entry at end
   - Maintain 20-entry limit

2. When loading new image:
   - Clear all entries
   - Reset history to empty state
   - Clear point selection collection
   - Exit point selection mode
   - Disable undo button

### Point Selection Cancellation Flow

1. User is in point selection mode with points selected
2. User clicks "Cancel" button
3. Controller clears `PointSelectionCollection`
4. Controller exits point selection mode
5. Controller emits signal to disable point selection in `ImageView`
6. `ImageView` removes all visual markers
7. Image returns to previous state (before point selection mode)

## Constraints

- **Memory**: Maximum ~240MB for operation history (20 entries × ~12MB per 2000x2000px RGBA image). Point selection collection is minimal memory (few KB for coordinates).
- **Persistence**: No persistence - history and point selection are session-only (cleared on app restart)
- **Scope**: Only tracks complex button-based operations, NOT slider changes
- **Limit**: Fixed at 20 operations (rolling history). No limit on number of points user can select (but UI should guide reasonable usage)
- **Coordinate System**: Point coordinates must be captured in image pixel space, accounting for any scaling/positioning in the displayed view

## Future Enhancements (Out of Scope)

- Redo functionality (forward history)
- Operation history persistence (save/load)
- Selective undo (undo specific operation, not just last)
- Operation preview/thumbnail in history
- Memory optimization (store only pixel differences)

