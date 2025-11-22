"""Point selection model for interactive background removal."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PointSelection:
    """Represents a single point selected by the user on the image during background removal.

    This model stores the coordinates and label (keep/remove) for a point clicked
    by the user during point selection mode. Coordinates are in image pixel space.

    Attributes:
        x: X coordinate of the point in image pixel space (0 to image width).
        y: Y coordinate of the point in image pixel space (0 to image height).
        label: Label indicating whether point is "keep" (foreground) or "remove" (background).

    Raises:
        ValueError: If label is not "keep" or "remove", or if coordinates are negative.
    """

    x: int
    y: int
    label: str

    def __post_init__(self) -> None:
        """Validate point selection after initialization.

        Validates that label is either "keep" or "remove", and that coordinates
        are non-negative. Coordinate bounds validation (against image dimensions)
        should be performed by the collection or controller that has access to
        image dimensions.
        """
        if self.label not in ("keep", "remove"):
            raise ValueError(f'label must be "keep" or "remove", got: {self.label}')
        if self.x < 0:
            raise ValueError(f"x coordinate must be >= 0, got: {self.x}")
        if self.y < 0:
            raise ValueError(f"y coordinate must be >= 0, got: {self.y}")


class PointSelectionCollection:
    """Collection of points selected during point selection mode.

    Manages a list of PointSelection instances and provides methods to add,
    remove, query, and convert points to SAM prompt format for background removal.

    Attributes:
        points: List of selected points with their coordinates and labels.
        is_active: Whether point selection mode is currently active.
    """

    def __init__(self) -> None:
        """Initialize empty point selection collection."""
        self.points: List[PointSelection] = []
        self.is_active: bool = False

    def add_point(self, x: int, y: int, label: str) -> None:
        """Add new point to collection.

        Args:
            x: X coordinate of the point in image pixel space.
            y: Y coordinate of the point in image pixel space.
            label: Label indicating whether point is "keep" (foreground) or "remove" (background).

        Raises:
            ValueError: If label is invalid or coordinates are negative.
        """
        point = PointSelection(x=x, y=y, label=label)
        self.points.append(point)

    def remove_point(self, x: int, y: int) -> None:
        """Remove point at specific coordinates (if exists).

        Args:
            x: X coordinate of the point to remove.
            y: Y coordinate of the point to remove.
        """
        self.points = [p for p in self.points if not (p.x == x and p.y == y)]

    def clear(self) -> None:
        """Remove all points from collection."""
        self.points.clear()

    def get_keep_points(self) -> List[PointSelection]:
        """Get all points labeled "keep".

        Returns:
            List of PointSelection instances with label "keep".
        """
        return [p for p in self.points if p.label == "keep"]

    def get_remove_points(self) -> List[PointSelection]:
        """Get all points labeled "remove".

        Returns:
            List of PointSelection instances with label "remove".
        """
        return [p for p in self.points if p.label == "remove"]

    def get_count(self) -> int:
        """Get total number of points in collection.

        Returns:
            Total number of points.
        """
        return len(self.points)

    def to_sam_prompts(self) -> List[Dict[str, Any]]:
        """Convert points to SAM prompt format for rembg.

        Converts PointSelection instances to SAM prompt format:
        - "keep" label -> label: 1 (foreground)
        - "remove" label -> label: 0 (background)

        Returns:
            List of prompt dictionaries in SAM format:
            [{"type": "point", "data": [x, y], "label": 1/0}, ...]
        """
        prompts = []
        for point in self.points:
            # Convert label: "keep" -> 1, "remove" -> 0
            sam_label = 1 if point.label == "keep" else 0
            prompts.append(
                {
                    "type": "point",
                    "data": [point.x, point.y],
                    "label": sam_label,
                }
            )
        return prompts

