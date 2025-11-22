"""Unit tests for ImageLoader service."""

from pathlib import Path

import pytest
import numpy as np
from PIL import Image as PILImage

from src.models.image_model import ImageModel
from src.services.image_loader import ImageLoader
from src.services import ImageLoadError, ImageValidationError


class TestImageLoader:
    """Tests for ImageLoader service."""

    def test_validate_image_format_supported(self, sample_image_path: Path) -> None:
        """Test validate_image_format accepts supported formats."""
        loader = ImageLoader()
        assert loader.validate_image_format(str(sample_image_path)) is True

    def test_validate_image_format_unsupported(self, tmp_path: Path) -> None:
        """Test validate_image_format rejects unsupported formats."""
        loader = ImageLoader()
        unsupported_file = tmp_path / "test.txt"
        unsupported_file.write_text("not an image")

        with pytest.raises(ImageValidationError, match="Unsupported file format"):
            loader.validate_image_format(str(unsupported_file))

    def test_validate_image_format_case_insensitive(self, tmp_path: Path) -> None:
        """Test validate_image_format is case insensitive."""
        loader = ImageLoader()
        # Create image with uppercase extension
        image = PILImage.new("RGB", (100, 100))
        image_path = tmp_path / "test.PNG"
        image.save(image_path)

        assert loader.validate_image_format(str(image_path)) is True

    def test_validate_image_size_within_limits(self, sample_image_model: ImageModel) -> None:
        """Test validate_image_size accepts images within limits."""
        loader = ImageLoader()
        assert loader.validate_image_size(sample_image_model) is True

    def test_validate_image_size_exceeds_width(self, tmp_path: Path) -> None:
        """Test validate_image_size rejects images exceeding width limit."""
        loader = ImageLoader()
        # Create 2001x1000 image
        image = PILImage.new("RGB", (2001, 1000))
        image_path = tmp_path / "wide_image.png"
        image.save(image_path)

        # Loading should fail because ImageModel validation happens first
        with pytest.raises(ImageLoadError, match="exceeds maximum"):
            loader.load_image(str(image_path))

    def test_validate_image_size_exceeds_height(self, tmp_path: Path) -> None:
        """Test validate_image_size rejects images exceeding height limit."""
        loader = ImageLoader()
        # Create 1000x2001 image
        image = PILImage.new("RGB", (1000, 2001))
        image_path = tmp_path / "tall_image.png"
        image.save(image_path)

        # Loading should fail because ImageModel validation happens first
        with pytest.raises(ImageLoadError, match="exceeds maximum"):
            loader.load_image(str(image_path))

    def test_load_image_success(self, sample_image_path: Path) -> None:
        """Test load_image successfully loads a valid image."""
        loader = ImageLoader()
        image = loader.load_image(str(sample_image_path))

        assert isinstance(image, ImageModel)
        assert image.width == 100
        assert image.height == 100
        # Format might be "PNG" or "UNKNOWN" depending on PIL version
        assert image.format in ("PNG", "UNKNOWN")
        assert image.has_alpha is False
        assert image.pixel_data.shape == (100, 100, 3)

    def test_load_image_rgba(self, sample_rgba_image_path: Path) -> None:
        """Test load_image loads RGBA images correctly."""
        loader = ImageLoader()
        image = loader.load_image(str(sample_rgba_image_path))

        assert image.has_alpha is True
        assert image.pixel_data.shape == (100, 100, 4)

    def test_load_image_file_not_found(self) -> None:
        """Test load_image raises error for non-existent file."""
        loader = ImageLoader()
        with pytest.raises(ImageLoadError, match="File not found"):
            loader.load_image("/nonexistent/path/image.png")

    def test_load_image_unsupported_format(self, tmp_path: Path) -> None:
        """Test load_image raises error for unsupported format."""
        loader = ImageLoader()
        text_file = tmp_path / "test.txt"
        text_file.write_text("not an image")

        with pytest.raises(ImageValidationError, match="Unsupported file format"):
            loader.load_image(str(text_file))

    def test_load_image_corrupted_file(self, tmp_path: Path) -> None:
        """Test load_image raises error for corrupted image file."""
        loader = ImageLoader()
        # Create a file that looks like an image but is corrupted
        corrupted_file = tmp_path / "corrupted.png"
        corrupted_file.write_bytes(b"PNG\x00\x01\x02\x03\xFF\xFF\xFF\xFF")

        with pytest.raises(ImageLoadError, match="Corrupted or unreadable"):
            loader.load_image(str(corrupted_file))

    def test_load_image_converts_to_rgb(self, tmp_path: Path) -> None:
        """Test load_image converts non-RGB modes to RGB."""
        loader = ImageLoader()
        # Create a grayscale image (mode 'L')
        image = PILImage.new("L", (50, 50), color=128)
        image_path = tmp_path / "grayscale.png"
        image.save(image_path)

        loaded_image = loader.load_image(str(image_path))
        assert loaded_image.pixel_data.shape[2] == 3  # Should be RGB
        assert loaded_image.has_alpha is False

    def test_load_image_preserves_original_data(self, sample_image_path: Path) -> None:
        """Test load_image preserves original pixel data separately."""
        loader = ImageLoader()
        image = loader.load_image(str(sample_image_path))

        # Original and current should be equal initially
        assert np.array_equal(image.pixel_data, image.original_pixel_data)
        # But they should be separate arrays (not the same object)
        assert image.pixel_data is not image.original_pixel_data

    def test_load_image_maximum_size(self, tmp_path: Path) -> None:
        """Test load_image accepts images at maximum size (2000x2000)."""
        loader = ImageLoader()
        # Create 2000x2000 image
        image = PILImage.new("RGB", (2000, 2000))
        image_path = tmp_path / "max_size.png"
        image.save(image_path)

        loaded_image = loader.load_image(str(image_path))
        assert loaded_image.width == 2000
        assert loaded_image.height == 2000

    def test_supported_formats(self) -> None:
        """Test SUPPORTED_FORMATS contains expected formats."""
        loader = ImageLoader()
        expected_formats = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        assert loader.SUPPORTED_FORMATS == expected_formats

    def test_max_dimension_constant(self) -> None:
        """Test MAX_DIMENSION constant is set correctly."""
        loader = ImageLoader()
        assert loader.MAX_DIMENSION == 2000

