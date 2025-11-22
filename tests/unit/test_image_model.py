"""Unit tests for ImageModel, ImageStatistics, and rgb_to_hex utility."""

import pytest
import numpy as np

from src.models.image_model import ImageModel, ImageStatistics, rgb_to_hex


class TestImageModel:
    """Tests for ImageModel class."""

    def test_create_valid_rgb_image(self) -> None:
        """Test creating ImageModel with valid RGB image."""
        width, height = 100, 100
        pixel_data = np.zeros((height, width, 3), dtype=np.uint8)
        original_pixel_data = pixel_data.copy()

        image = ImageModel(
            width=width,
            height=height,
            pixel_data=pixel_data,
            original_pixel_data=original_pixel_data,
            format="PNG",
            has_alpha=False,
        )

        assert image.width == width
        assert image.height == height
        assert image.format == "PNG"
        assert image.has_alpha is False
        assert np.array_equal(image.pixel_data, pixel_data)
        assert np.array_equal(image.original_pixel_data, original_pixel_data)

    def test_create_valid_rgba_image(self) -> None:
        """Test creating ImageModel with valid RGBA image."""
        width, height = 200, 150
        pixel_data = np.zeros((height, width, 4), dtype=np.uint8)
        original_pixel_data = pixel_data.copy()

        image = ImageModel(
            width=width,
            height=height,
            pixel_data=pixel_data,
            original_pixel_data=original_pixel_data,
            format="PNG",
            has_alpha=True,
        )

        assert image.width == width
        assert image.height == height
        assert image.has_alpha is True
        assert pixel_data.shape[2] == 4

    def test_validation_rejects_zero_width(self) -> None:
        """Test that ImageModel rejects zero width."""
        pixel_data = np.zeros((100, 100, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="Image dimensions must be greater than 0"):
            ImageModel(
                width=0,
                height=100,
                pixel_data=pixel_data,
                original_pixel_data=pixel_data.copy(),
                format="PNG",
                has_alpha=False,
            )

    def test_validation_rejects_zero_height(self) -> None:
        """Test that ImageModel rejects zero height."""
        pixel_data = np.zeros((100, 100, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="Image dimensions must be greater than 0"):
            ImageModel(
                width=100,
                height=0,
                pixel_data=pixel_data,
                original_pixel_data=pixel_data.copy(),
                format="PNG",
                has_alpha=False,
            )

    def test_validation_rejects_oversized_image(self) -> None:
        """Test that ImageModel rejects images exceeding 2000x2000px."""
        pixel_data = np.zeros((2001, 2000, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="Image size exceeds maximum"):
            ImageModel(
                width=2001,
                height=2000,
                pixel_data=pixel_data,
                original_pixel_data=pixel_data.copy(),
                format="PNG",
                has_alpha=False,
            )

    def test_validation_rejects_non_numpy_array(self) -> None:
        """Test that ImageModel rejects non-NumPy array pixel_data."""
        with pytest.raises(ValueError, match="pixel_data must be a NumPy array"):
            ImageModel(
                width=100,
                height=100,
                pixel_data=[[[0, 0, 0]]],  # Not a NumPy array
                original_pixel_data=np.zeros((100, 100, 3), dtype=np.uint8),
                format="PNG",
                has_alpha=False,
            )

    def test_validation_rejects_invalid_shape(self) -> None:
        """Test that ImageModel rejects pixel_data with invalid shape."""
        # 2D array instead of 3D
        pixel_data = np.zeros((100, 100), dtype=np.uint8)

        with pytest.raises(ValueError, match="pixel_data must have shape"):
            ImageModel(
                width=100,
                height=100,
                pixel_data=pixel_data,
                original_pixel_data=pixel_data.copy(),
                format="PNG",
                has_alpha=False,
            )

    def test_validation_rejects_invalid_channels(self) -> None:
        """Test that ImageModel rejects pixel_data with invalid channel count."""
        # 5 channels instead of 3 or 4
        pixel_data = np.zeros((100, 100, 5), dtype=np.uint8)

        with pytest.raises(ValueError, match="pixel_data must have 3 \\(RGB\\) or 4 \\(RGBA\\) channels"):
            ImageModel(
                width=100,
                height=100,
                pixel_data=pixel_data,
                original_pixel_data=pixel_data.copy(),
                format="PNG",
                has_alpha=False,
            )

    def test_accepts_maximum_size(self) -> None:
        """Test that ImageModel accepts images at maximum size (2000x2000)."""
        pixel_data = np.zeros((2000, 2000, 3), dtype=np.uint8)

        image = ImageModel(
            width=2000,
            height=2000,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        assert image.width == 2000
        assert image.height == 2000


class TestImageStatistics:
    """Tests for ImageStatistics class."""

    def test_create_valid_statistics(self) -> None:
        """Test creating ImageStatistics with valid data."""
        stats = ImageStatistics(
            distinct_color_count=256,
            width=100,
            height=100,
            hover_hex_color=None,
        )

        assert stats.distinct_color_count == 256
        assert stats.width == 100
        assert stats.height == 100
        assert stats.hover_hex_color is None

    def test_create_with_hex_color(self) -> None:
        """Test creating ImageStatistics with valid HEX color."""
        stats = ImageStatistics(
            distinct_color_count=128,
            width=200,
            height=150,
            hover_hex_color="#FF5733",
        )

        assert stats.hover_hex_color == "#FF5733"

    def test_create_with_rgba_hex_color(self) -> None:
        """Test creating ImageStatistics with valid RGBA HEX color."""
        stats = ImageStatistics(
            distinct_color_count=64,
            width=50,
            height=50,
            hover_hex_color="#FF5733FF",
        )

        assert stats.hover_hex_color == "#FF5733FF"

    def test_validation_rejects_zero_color_count(self) -> None:
        """Test that ImageStatistics rejects zero distinct_color_count."""
        with pytest.raises(ValueError, match="distinct_color_count must be >= 1"):
            ImageStatistics(
                distinct_color_count=0,
                width=100,
                height=100,
            )

    def test_validation_rejects_invalid_hex_format(self) -> None:
        """Test that ImageStatistics rejects invalid HEX format."""
        with pytest.raises(ValueError, match="hover_hex_color must be valid HEX format"):
            ImageStatistics(
                distinct_color_count=256,
                width=100,
                height=100,
                hover_hex_color="FF5733",  # Missing #
            )

    def test_validation_rejects_hex_without_hash(self) -> None:
        """Test that ImageStatistics rejects HEX without hash prefix."""
        with pytest.raises(ValueError):
            ImageStatistics(
                distinct_color_count=256,
                width=100,
                height=100,
                hover_hex_color="FF5733",
            )

    def test_validation_rejects_invalid_hex_length(self) -> None:
        """Test that ImageStatistics rejects HEX with invalid length."""
        with pytest.raises(ValueError):
            ImageStatistics(
                distinct_color_count=256,
                width=100,
                height=100,
                hover_hex_color="#FF573",  # 5 hex digits, should be 6 or 8
            )

    def test_validation_rejects_non_hex_characters(self) -> None:
        """Test that ImageStatistics rejects HEX with non-hex characters."""
        with pytest.raises(ValueError):
            ImageStatistics(
                distinct_color_count=256,
                width=100,
                height=100,
                hover_hex_color="#GG5733",  # G is not valid hex
            )


class TestRgbToHex:
    """Tests for rgb_to_hex utility function."""

    def test_rgb_to_hex_basic(self) -> None:
        """Test basic RGB to HEX conversion."""
        result = rgb_to_hex(255, 87, 51)
        assert result == "#FF5733"

    def test_rgb_to_hex_zero_values(self) -> None:
        """Test RGB to HEX with zero values."""
        result = rgb_to_hex(0, 0, 0)
        assert result == "#000000"

    def test_rgb_to_hex_max_values(self) -> None:
        """Test RGB to HEX with maximum values."""
        result = rgb_to_hex(255, 255, 255)
        assert result == "#FFFFFF"

    def test_rgb_to_hex_lowercase_hex(self) -> None:
        """Test RGB to HEX produces uppercase hex digits."""
        result = rgb_to_hex(170, 187, 204)
        assert result == "#AABBCC"

    def test_rgba_to_hex_with_alpha(self) -> None:
        """Test RGBA to HEX conversion with alpha channel."""
        result = rgb_to_hex(255, 87, 51, 255)
        assert result == "#FF5733FF"

    def test_rgba_to_hex_transparent(self) -> None:
        """Test RGBA to HEX with transparent alpha."""
        result = rgb_to_hex(255, 87, 51, 0)
        assert result == "#FF573300"

    def test_rgba_to_hex_partial_alpha(self) -> None:
        """Test RGBA to HEX with partial alpha."""
        result = rgb_to_hex(255, 87, 51, 128)
        assert result == "#FF573380"

    def test_rgb_to_hex_single_digit_hex(self) -> None:
        """Test RGB to HEX with values requiring single digit hex."""
        result = rgb_to_hex(1, 15, 16)
        assert result == "#010F10"

