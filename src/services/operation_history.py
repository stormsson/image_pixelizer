"""Operation history management for undo functionality."""

import time
from dataclasses import dataclass
from typing import List, Optional

from src.models.image_model import ImageModel


@dataclass
class OperationHistoryEntry:
    """Represents a single entry in the operation history for undo functionality.

    Attributes:
        operation_type: Type of operation that was applied (e.g., "remove_background").
            Used to identify which operation to undo.
        image_state: Snapshot of the image state before the operation was applied.
            Contains full pixel data, dimensions, format, and transparency information.
        timestamp: Timestamp when the operation was recorded (for debugging/logging
            purposes). Uses time.time() format.
    """

    operation_type: str
    image_state: ImageModel
    timestamp: float

    def __post_init__(self) -> None:
        """Validate operation history entry after initialization.

        Validates that operation_type is not empty and image_state is valid.
        """
        if not self.operation_type:
            raise ValueError("operation_type must not be empty")
        if not isinstance(self.image_state, ImageModel):
            raise ValueError("image_state must be a valid ImageModel instance")


class OperationHistoryManager:
    """Manages operation history for undo functionality.

    Maintains a rolling history of up to 20 operations, with the oldest
    operations removed when the limit is reached. Each entry contains a
    snapshot of the image state before a complex operation was applied.
    """

    def __init__(self, max_size: int = 20) -> None:
        """Initialize operation history manager.

        Args:
            max_size: Maximum number of operations to store (default 20)
        """
        self._entries: List[OperationHistoryEntry] = []
        self._max_size = max_size

    def add_operation(
        self, operation_type: str, image_state: ImageModel
    ) -> None:
        """Add a new operation to the history.

        Creates an OperationHistoryEntry and adds it to the history.
        If the history is at max_size, removes the oldest entry first.

        Args:
            operation_type: Type of operation (e.g., "remove_background")
            image_state: Snapshot of image state before the operation
        """
        # Create a deep copy of the image state to avoid reference issues
        import copy

        copied_image_state = ImageModel(
            width=image_state.width,
            height=image_state.height,
            pixel_data=image_state.pixel_data.copy(),
            original_pixel_data=image_state.original_pixel_data.copy(),
            format=image_state.format,
            has_alpha=image_state.has_alpha,
        )

        entry = OperationHistoryEntry(
            operation_type=operation_type,
            image_state=copied_image_state,
            timestamp=time.time(),
        )

        # Add to end (most recent)
        self._entries.append(entry)

        # Remove oldest if limit reached
        if len(self._entries) > self._max_size:
            self._entries.pop(0)

    def can_undo(self) -> bool:
        """Check if undo is available.

        Returns:
            True if there are operations in history, False otherwise
        """
        return len(self._entries) > 0

    def get_last_operation(self) -> Optional[OperationHistoryEntry]:
        """Get the most recent operation entry without removing it.

        Returns:
            Most recent OperationHistoryEntry, or None if history is empty
        """
        if not self._entries:
            return None
        return self._entries[-1]

    def pop_last_operation(self) -> Optional[OperationHistoryEntry]:
        """Remove and return the most recent operation entry.

        Returns:
            Most recent OperationHistoryEntry, or None if history is empty
        """
        if not self._entries:
            return None
        return self._entries.pop()

    def clear(self) -> None:
        """Clear all operations from history."""
        self._entries.clear()

    def get_count(self) -> int:
        """Get the current number of operations in history.

        Returns:
            Number of operations currently stored
        """
        return len(self._entries)

