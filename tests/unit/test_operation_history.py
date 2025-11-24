"""Unit tests for OperationHistoryEntry dataclass."""

import time

import pytest
import numpy as np

from src.models.image_model import ImageModel
from src.services.operation_history import OperationHistoryEntry


class TestOperationHistoryEntry:
    """Tests for OperationHistoryEntry dataclass."""

    def test_create_valid_entry(self, sample_image_model: ImageModel) -> None:
        """Test creating OperationHistoryEntry with valid data."""
        timestamp = time.time()
        entry = OperationHistoryEntry(
            operation_type="remove_background",
            image_state=sample_image_model,
            timestamp=timestamp,
        )

        assert entry.operation_type == "remove_background"
        assert entry.image_state == sample_image_model
        assert entry.timestamp == timestamp

    def test_create_entry_with_rgba_image(self, sample_rgba_image_model: ImageModel) -> None:
        """Test creating OperationHistoryEntry with RGBA image."""
        timestamp = time.time()
        entry = OperationHistoryEntry(
            operation_type="remove_background",
            image_state=sample_rgba_image_model,
            timestamp=timestamp,
        )

        assert entry.operation_type == "remove_background"
        assert entry.image_state == sample_rgba_image_model
        assert entry.timestamp == timestamp
        assert entry.image_state.has_alpha is True

    def test_operation_type_validation_empty_string(self, sample_image_model: ImageModel) -> None:
        """Test that empty operation_type raises ValueError."""
        timestamp = time.time()

        with pytest.raises(ValueError, match="operation_type must not be empty"):
            OperationHistoryEntry(
                operation_type="",
                image_state=sample_image_model,
                timestamp=timestamp,
            )

    def test_operation_type_validation_whitespace_only(self, sample_image_model: ImageModel) -> None:
        """Test that whitespace-only operation_type is accepted (not validated)."""
        timestamp = time.time()
        entry = OperationHistoryEntry(
            operation_type="   ",
            image_state=sample_image_model,
            timestamp=timestamp,
        )

        assert entry.operation_type == "   "
        assert entry.image_state == sample_image_model
        assert entry.timestamp == timestamp

    def test_image_state_validation_none(self) -> None:
        """Test that None image_state raises ValueError."""
        timestamp = time.time()

        with pytest.raises(ValueError, match="image_state must be a valid ImageModel instance"):
            OperationHistoryEntry(
                operation_type="remove_background",
                image_state=None,  # type: ignore
                timestamp=timestamp,
            )

    def test_image_state_validation_invalid_type(self) -> None:
        """Test that invalid image_state type raises ValueError."""
        timestamp = time.time()

        with pytest.raises(ValueError, match="image_state must be a valid ImageModel instance"):
            OperationHistoryEntry(
                operation_type="remove_background",
                image_state="not an ImageModel",  # type: ignore
                timestamp=timestamp,
            )

    def test_timestamp_preserved(self, sample_image_model: ImageModel) -> None:
        """Test that timestamp is correctly preserved."""
        timestamp = 1234567890.123
        entry = OperationHistoryEntry(
            operation_type="remove_background",
            image_state=sample_image_model,
            timestamp=timestamp,
        )

        assert entry.timestamp == timestamp

    def test_different_operation_types(self, sample_image_model: ImageModel) -> None:
        """Test creating entries with different operation types."""
        timestamp = time.time()

        entry1 = OperationHistoryEntry(
            operation_type="remove_background",
            image_state=sample_image_model,
            timestamp=timestamp,
        )

        entry2 = OperationHistoryEntry(
            operation_type="crop",
            image_state=sample_image_model,
            timestamp=timestamp + 1,
        )

        assert entry1.operation_type == "remove_background"
        assert entry2.operation_type == "crop"

    def test_image_state_immutability(self, sample_image_model: ImageModel) -> None:
        """Test that image_state reference is preserved (not copied)."""
        timestamp = time.time()
        entry = OperationHistoryEntry(
            operation_type="remove_background",
            image_state=sample_image_model,
            timestamp=timestamp,
        )

        # Modifying the original should affect the entry (same reference)
        assert entry.image_state is sample_image_model

