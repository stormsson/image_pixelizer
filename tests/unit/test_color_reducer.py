"""Unit tests for ColorReducer service."""

import numpy as np
import pytest

from src.models.image_model import ImageModel
from src.services.color_reducer import ColorReducer


class TestColorReducer:
    """Tests for ColorReducer service."""

    def test_reduce_colors_basic(self) -> None:
        """Test basic color reduction with moderate sensitivity."""
        reducer = ColorReducer()

        # Create image with 4 distinct colors
        pixel_data = np.zeros((4, 4, 3), dtype=np.uint8)
        pixel_data[:2, :2] = [255, 0, 0]  # Red
        pixel_data[:2, 2:] = [0, 255, 0]  # Green
        pixel_data[2:, :2] = [0, 0, 255]  # Blue
        pixel_data[2:, 2:] = [255, 255, 0]  # Yellow

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, sensitivity=0.5)

        assert isinstance(result, ImageModel)
        assert result.width == 4
        assert result.height == 4
        assert result.pixel_data.shape == (4, 4, 3)
        assert result.format == "PNG"
        assert result.has_alpha == False

    def test_reduce_colors_sensitivity_zero(self) -> None:
        """Test color reduction with sensitivity=0.0 (no reduction)."""
        reducer = ColorReducer()

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

        result = reducer.reduce_colors(image, sensitivity=0.0)

        # With sensitivity 0, should return original image
        assert np.array_equal(result.pixel_data, pixel_data)

    def test_reduce_colors_sensitivity_one(self) -> None:
        """Test color reduction with sensitivity=1.0 (maximum reduction)."""
        reducer = ColorReducer()

        # Create image with many similar colors
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        for i in range(10):
            for j in range(10):
                pixel_data[i, j] = [i * 25, j * 25, (i + j) * 12]

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, sensitivity=1.0)

        # Should have fewer distinct colors than original
        original_colors = ColorReducer.count_distinct_colors(pixel_data)
        result_colors = ColorReducer.count_distinct_colors(result.pixel_data)
        assert result_colors <= original_colors

    def test_reduce_colors_rgba_image(self) -> None:
        """Test color reduction with RGBA image (preserves alpha)."""
        reducer = ColorReducer()

        pixel_data = np.zeros((4, 4, 4), dtype=np.uint8)
        pixel_data[:, :, :3] = [255, 0, 0]  # Red RGB
        pixel_data[:, :, 3] = 255  # Full alpha

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        result = reducer.reduce_colors(image, sensitivity=0.5)

        assert result.has_alpha == True
        assert result.pixel_data.shape == (4, 4, 4)
        # Alpha channel should be preserved
        assert np.all(result.pixel_data[:, :, 3] == 255)

    def test_reduce_colors_invalid_sensitivity(self) -> None:
        """Test color reduction with invalid sensitivity values."""
        reducer = ColorReducer()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        with pytest.raises(ValueError, match="sensitivity must be between 0.0 and 1.0"):
            reducer.reduce_colors(image, sensitivity=-0.1)

        with pytest.raises(ValueError, match="sensitivity must be between 0.0 and 1.0"):
            reducer.reduce_colors(image, sensitivity=1.1)

    def test_reduce_colors_creates_new_array(self) -> None:
        """Test that color reduction creates a new array (immutability)."""
        reducer = ColorReducer()

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

        result = reducer.reduce_colors(image, sensitivity=0.5)

        # Should be a new array, not the same reference
        assert result.pixel_data is not pixel_data
        assert result.pixel_data is not image.pixel_data

    def test_reduce_colors_reduces_color_count(self) -> None:
        """Test that color reduction actually reduces distinct color count."""
        reducer = ColorReducer()

        # Create image with many similar colors (gradient)
        pixel_data = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            for j in range(20):
                pixel_data[i, j] = [i * 12, j * 12, (i + j) * 6]

        image = ImageModel(
            width=20,
            height=20,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        original_count = ColorReducer.count_distinct_colors(pixel_data)
        result = reducer.reduce_colors(image, sensitivity=0.7)
        result_count = ColorReducer.count_distinct_colors(result.pixel_data)

        # Should have fewer or equal colors
        assert result_count <= original_count
        # With sensitivity 0.7, should have significantly fewer colors
        assert result_count < original_count

    def test_reduce_colors_higher_sensitivity_more_reduction(self) -> None:
        """Test that higher sensitivity produces more color reduction."""
        reducer = ColorReducer()

        # Create image with many colors
        pixel_data = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            for j in range(20):
                pixel_data[i, j] = [i * 12, j * 12, (i + j) * 6]

        image = ImageModel(
            width=20,
            height=20,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result_low = reducer.reduce_colors(image, sensitivity=0.3)
        result_high = reducer.reduce_colors(image, sensitivity=0.8)

        count_low = ColorReducer.count_distinct_colors(result_low.pixel_data)
        count_high = ColorReducer.count_distinct_colors(result_high.pixel_data)

        # Higher sensitivity should result in fewer colors
        assert count_high <= count_low

    def test_count_distinct_colors_basic(self) -> None:
        """Test counting distinct colors in image."""
        pixel_data = np.zeros((4, 4, 3), dtype=np.uint8)
        pixel_data[:2, :2] = [255, 0, 0]  # Red
        pixel_data[:2, 2:] = [0, 255, 0]  # Green
        pixel_data[2:, :2] = [0, 0, 255]  # Blue
        pixel_data[2:, 2:] = [255, 255, 0]  # Yellow

        count = ColorReducer.count_distinct_colors(pixel_data)
        assert count == 4

    def test_count_distinct_colors_uniform(self) -> None:
        """Test counting distinct colors in uniform image."""
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [100, 150, 200]

        count = ColorReducer.count_distinct_colors(pixel_data)
        assert count == 1

    def test_count_distinct_colors_rgba(self) -> None:
        """Test counting distinct colors in RGBA image."""
        pixel_data = np.zeros((4, 4, 4), dtype=np.uint8)
        pixel_data[:2, :2, :3] = [255, 0, 0]  # Red
        pixel_data[:2, :2, 3] = 255  # Alpha
        pixel_data[2:, 2:, :3] = [0, 255, 0]  # Green
        pixel_data[2:, 2:, 3] = 128  # Different alpha
        # Remaining pixels are [0, 0, 0, 0] (black with alpha 0)

        count = ColorReducer.count_distinct_colors(pixel_data)
        # Should count RGBA tuples: red+alpha255, green+alpha128, and black+alpha0
        assert count == 3

    def test_count_distinct_colors_empty(self) -> None:
        """Test counting distinct colors in empty image."""
        pixel_data = np.zeros((0, 0, 3), dtype=np.uint8)

        count = ColorReducer.count_distinct_colors(pixel_data)
        assert count == 0

