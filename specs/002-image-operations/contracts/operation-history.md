# Contract: OperationHistoryManager Service

**Service**: `src/services/operation_history.py`  
**Feature**: Image Operations in Controls Panel  
**Date**: 2025-01-27

## Purpose

Service for managing operation history to support undo functionality. Tracks complex button-based operations (not slider changes) with a maximum of 20 entries using rolling history.

## Interface

### Class: `OperationHistoryManager`

```python
class OperationHistoryManager:
    """Manages operation history for undo functionality."""
    
    def __init__(self, max_size: int = 20) -> None:
        """
        Initialize operation history manager.
        
        Args:
            max_size: Maximum number of operations to track (default 20)
        """
    
    def add_operation(
        self, 
        operation_type: str, 
        image_state: ImageModel
    ) -> None:
        """
        Add operation to history.
        
        Args:
            operation_type: Type of operation (e.g., "remove_background")
            image_state: ImageModel snapshot before operation was applied
            
        Raises:
            ValueError: If operation_type is empty or image_state is invalid
        """
    
    def can_undo(self) -> bool:
        """
        Check if undo is available.
        
        Returns:
            True if at least one operation is in history
        """
    
    def get_last_operation(self) -> Optional[OperationHistoryEntry]:
        """
        Get last operation without removing it.
        
        Returns:
            OperationHistoryEntry or None if history is empty
        """
    
    def pop_last_operation(self) -> Optional[OperationHistoryEntry]:
        """
        Remove and return last operation (for undo).
        
        Returns:
            OperationHistoryEntry or None if history is empty
        """
    
    def clear(self) -> None:
        """Clear all operation history."""
    
    def get_count(self) -> int:
        """
        Get current number of operations in history.
        
        Returns:
            Number of operations (0 to max_size)
        """
```

### Class: `OperationHistoryEntry`

```python
@dataclass
class OperationHistoryEntry:
    """Represents a single operation in history."""
    
    operation_type: str
    image_state: ImageModel
    timestamp: float
```

## Behavior

### History Management

- **Maximum Size**: Fixed at 20 operations (configurable via constructor, default 20)
- **Rolling History**: When 21st operation is added, oldest entry (index 0) is removed
- **Order**: Most recent operation is always at end of list (LIFO - Last In First Out)
- **Clear on Load**: History is cleared when new image is loaded

### Operation Types

Tracked operation types:
- `"remove_background"` - Background removal operation

Future operation types can be added (e.g., `"crop"`, `"rotate"`, etc.)

**NOT Tracked**:
- Pixelization slider changes
- Color sensitivity slider changes
- Any slider-based operations

### Image State Snapshots

- **Full Snapshot**: Complete `ImageModel` copy (pixel_data, dimensions, format, etc.)
- **Memory Usage**: ~12MB per 2000x2000px RGBA image
- **Total Memory**: ~240MB maximum (20 operations × 12MB)

### Validation

- `operation_type` must not be empty string
- `image_state` must be valid `ImageModel` instance
- `max_size` must be positive integer

## Error Handling

**ValueError**:
- Raised when `operation_type` is empty
- Raised when `image_state` is None or invalid
- User message: "Invalid operation data"

**No Exceptions**:
- `get_last_operation()` and `pop_last_operation()` return `None` if history is empty (no exceptions)
- `can_undo()` returns `False` if history is empty

## Performance Requirements

- **Add Operation**: O(1) amortized (list append, occasional removal of oldest)
- **Pop Operation**: O(1) (list pop from end)
- **Clear**: O(n) where n is number of entries (typically <20)
- **Memory**: Bounded by max_size × image_size

## Dependencies

- **ImageModel**: Existing model from `src.models.image_model`
- **dataclasses**: For `OperationHistoryEntry` (Python standard library)

## Testing Requirements

### Unit Tests

- Test adding operations (up to limit)
- Test rolling history (21st operation removes oldest)
- Test `can_undo()` returns correct state
- Test `get_last_operation()` returns most recent
- Test `pop_last_operation()` removes and returns most recent
- Test `clear()` removes all entries
- Test `get_count()` returns correct count
- Test validation (empty operation_type, invalid image_state)
- Test with max_size = 1, 5, 20, 100 (boundary testing)

### Integration Tests

- Test integration with controller (add → pop → verify)
- Test clear on new image load
- Test memory usage with large images

## Example Usage

```python
from src.services.operation_history import OperationHistoryManager
from src.models.image_model import ImageModel

history = OperationHistoryManager(max_size=20)

# Add operation
history.add_operation("remove_background", image_snapshot)

# Check if undo available
if history.can_undo():
    # Get last operation for undo
    last_entry = history.pop_last_operation()
    restored_image = last_entry.image_state

# Clear history
history.clear()
```

## Notes

- History is in-memory only (no persistence)
- History is cleared when application closes
- Each entry stores full image snapshot (not just differences)
- Memory optimization (storing differences) is future enhancement
- Thread-safe for single-threaded Qt application (no concurrent access expected)

