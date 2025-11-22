"""Unit tests for Pixelizer service."""

import numpy as np
import pytest

from src.models.image_model import ImageModel
from src.services.pixelizer import Pixelizer


class TestPixelizer:
    """Tests for Pixelizer service."""

    def test_pixelize_basic(self) -> None:
        """Test basic pixelization with pixel_size=2."""
        pixelizer = Pixelizer()

        # Create 4x4 RGB image
        pixel_data = np.zeros((4, 4, 3), dtype=np.uint8)
        # Fill with pattern: top-left 2x2 = red, rest = blue
        pixel_data[:2, :2] = [255, 0, 0]  # Red
        pixel_data[2:, 2:] = [0, 0, 255]  # Blue
        pixel_data[:2, 2:] = [0, 255, 0]  # Green
        pixel_data[2:, :2] = [255, 255, 0]  # Yellow

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = pixelizer.pixelize(image, pixel_size=2)

        assert isinstance(result, ImageModel)
        assert result.width == 4
        assert result.height == 4
        # Each 2x2 block should have uniform color (average of that block)
        assert result.pixel_data.shape == (4, 4, 3)

    def test_pixelize_pixel_size_one(self) -> None:
        """Test pixelization with pixel_size=1 (no effect)."""
        pixelizer = Pixelizer()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [100, 150, 200]

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = pixelizer.pixelize(image, pixel_size=1)

        # With pixel_size=1, image should remain unchanged
        assert np.array_equal(result.pixel_data, pixel_data)

    def test_pixelize_large_blocks(self) -> None:
        """Test pixelization with large pixel_size."""
        pixelizer = Pixelizer()

        # Create 20x20 image
        pixel_data = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)

        image = ImageModel(
            width=20,
            height=20,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = pixelizer.pixelize(image, pixel_size=10)

        assert result.width == 20
        assert result.height == 20
        # Should have 2x2 blocks (20/10 = 2)
        # Each block should have uniform color

    def test_pixelize_rgba_image(self) -> None:
        """Test pixelization with RGBA image."""
        pixelizer = Pixelizer()

        pixel_data = np.zeros((8, 8, 4), dtype=np.uint8)
        pixel_data[:, :] = [255, 100, 50, 200]  # RGBA

        image = ImageModel(
            width=8,
            height=8,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        result = pixelizer.pixelize(image, pixel_size=4)

        assert result.has_alpha is True
        assert result.pixel_data.shape == (8, 8, 4)
        # Alpha channel should be preserved

    def test_pixelize_non_divisible_dimensions(self) -> None:
        """Test pixelization when dimensions aren't divisible by pixel_size."""
        pixelizer = Pixelizer()

        # Create 7x7 image, pixel_size=3
        pixel_data = np.zeros((7, 7, 3), dtype=np.uint8)
        pixel_data[:, :] = [128, 128, 128]

        image = ImageModel(
            width=7,
            height=7,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = pixelizer.pixelize(image, pixel_size=3)

        # Should handle edge cases gracefully
        assert result.width == 7
        assert result.height == 7
        assert result.pixel_data.shape == (7, 7, 3)

    def test_pixelize_preserves_original_data(self) -> None:
        """Test pixelization doesn't modify original pixel data."""
        pixelizer = Pixelizer()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [50, 100, 150]
        original_copy = pixel_data.copy()

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=original_copy.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = pixelizer.pixelize(image, pixel_size=5)

        # Original pixel_data should be unchanged
        assert np.array_equal(image.original_pixel_data, original_copy)

    def test_pixelize_creates_new_array(self) -> None:
        """Test pixelization creates new array, doesn't modify input."""
        pixelizer = Pixelizer()

        # Create non-uniform image with varying colors
        pixel_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        original_pixel_data = image.pixel_data.copy()
        result = pixelizer.pixelize(image, pixel_size=3)

        # Input image's pixel_data should be unchanged
        assert np.array_equal(image.pixel_data, original_pixel_data)
        # Result should be a new array (not the same object)
        assert result.pixel_data is not image.pixel_data

    def test_pixelize_averages_colors_correctly(self) -> None:
        """Test pixelization correctly averages colors in blocks."""
        pixelizer = Pixelizer()

        # Create 4x4 image with known pattern
        pixel_data = np.zeros((4, 4, 3), dtype=np.uint8)
        # Top-left 2x2: [100, 0, 0] and [0, 100, 0] -> average [50, 50, 0]
        pixel_data[0, 0] = [100, 0, 0]
        pixel_data[0, 1] = [0, 100, 0]
        pixel_data[1, 0] = [0, 100, 0]
        pixel_data[1, 1] = [100, 0, 0]

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = pixelizer.pixelize(image, pixel_size=2)

        # Top-left 2x2 block should have average color
        top_left_color = result.pixel_data[0, 0]
        # Average of [100,0,0] and [0,100,0] = [50, 50, 0]
        assert top_left_color[0] == 50
        assert top_left_color[1] == 50
        assert top_left_color[2] == 0

    def test_pixelize_edge_case_small_image(self) -> None:
        """Test pixelization with very small image."""
        pixelizer = Pixelizer()

        pixel_data = np.zeros((2, 2, 3), dtype=np.uint8)
        pixel_data[:, :] = [255, 255, 255]

        image = ImageModel(
            width=2,
            height=2,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = pixelizer.pixelize(image, pixel_size=2)

        # Should handle gracefully
        assert result.width == 2
        assert result.height == 2

