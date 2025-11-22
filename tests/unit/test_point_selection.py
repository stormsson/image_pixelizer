"""Unit tests for PointSelection dataclass."""

import pytest

from src.models.point_selection import PointSelection


class TestPointSelection:
    """Tests for PointSelection dataclass."""

    def test_create_valid_keep_point(self) -> None:
        """Test creating PointSelection with valid keep label."""
        point = PointSelection(x=50, y=75, label="keep")

        assert point.x == 50
        assert point.y == 75
        assert point.label == "keep"

    def test_create_valid_remove_point(self) -> None:
        """Test creating PointSelection with valid remove label."""
        point = PointSelection(x=100, y=200, label="remove")

        assert point.x == 100
        assert point.y == 200
        assert point.label == "remove"

    def test_create_point_at_origin(self) -> None:
        """Test creating PointSelection at origin (0, 0)."""
        point = PointSelection(x=0, y=0, label="keep")

        assert point.x == 0
        assert point.y == 0
        assert point.label == "keep"

    def test_create_point_large_coordinates(self) -> None:
        """Test creating PointSelection with large coordinates."""
        point = PointSelection(x=1999, y=1999, label="remove")

        assert point.x == 1999
        assert point.y == 1999
        assert point.label == "remove"

    def test_label_validation_invalid_string(self) -> None:
        """Test that invalid label string raises ValueError."""
        with pytest.raises(ValueError, match='label must be "keep" or "remove"'):
            PointSelection(x=50, y=75, label="invalid")

    def test_label_validation_empty_string(self) -> None:
        """Test that empty label string raises ValueError."""
        with pytest.raises(ValueError, match='label must be "keep" or "remove"'):
            PointSelection(x=50, y=75, label="")

    def test_label_validation_case_sensitive(self) -> None:
        """Test that label validation is case-sensitive."""
        with pytest.raises(ValueError, match='label must be "keep" or "remove"'):
            PointSelection(x=50, y=75, label="Keep")

        with pytest.raises(ValueError, match='label must be "keep" or "remove"'):
            PointSelection(x=50, y=75, label="REMOVE")

    def test_x_coordinate_validation_negative(self) -> None:
        """Test that negative x coordinate raises ValueError."""
        with pytest.raises(ValueError, match="x coordinate must be >= 0"):
            PointSelection(x=-1, y=75, label="keep")

    def test_y_coordinate_validation_negative(self) -> None:
        """Test that negative y coordinate raises ValueError."""
        with pytest.raises(ValueError, match="y coordinate must be >= 0"):
            PointSelection(x=50, y=-1, label="keep")

    def test_both_coordinates_negative(self) -> None:
        """Test that both negative coordinates raise ValueError (x first)."""
        with pytest.raises(ValueError, match="x coordinate must be >= 0"):
            PointSelection(x=-1, y=-1, label="keep")

    def test_keep_label_preserved(self) -> None:
        """Test that keep label is correctly preserved."""
        point = PointSelection(x=10, y=20, label="keep")
        assert point.label == "keep"

    def test_remove_label_preserved(self) -> None:
        """Test that remove label is correctly preserved."""
        point = PointSelection(x=10, y=20, label="remove")
        assert point.label == "remove"

    def test_coordinates_preserved(self) -> None:
        """Test that coordinates are correctly preserved."""
        point = PointSelection(x=123, y=456, label="keep")
        assert point.x == 123
        assert point.y == 456

    def test_multiple_points_different_labels(self) -> None:
        """Test creating multiple points with different labels."""
        keep_point = PointSelection(x=50, y=50, label="keep")
        remove_point = PointSelection(x=100, y=100, label="remove")

        assert keep_point.label == "keep"
        assert remove_point.label == "remove"
        assert keep_point.x == 50
        assert remove_point.x == 100

    def test_point_equality(self) -> None:
        """Test that points with same values are equal."""
        point1 = PointSelection(x=50, y=75, label="keep")
        point2 = PointSelection(x=50, y=75, label="keep")

        assert point1 == point2

    def test_point_inequality_different_coordinates(self) -> None:
        """Test that points with different coordinates are not equal."""
        point1 = PointSelection(x=50, y=75, label="keep")
        point2 = PointSelection(x=51, y=75, label="keep")

        assert point1 != point2

    def test_point_inequality_different_labels(self) -> None:
        """Test that points with different labels are not equal."""
        point1 = PointSelection(x=50, y=75, label="keep")
        point2 = PointSelection(x=50, y=75, label="remove")

        assert point1 != point2

