"""Unit tests for ImageSaver service."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image as PILImage

from src.models.image_model import ImageModel
from src.services.image_saver import ImageSaver, ImageSaveError


class TestImageSaver:
    """Tests for ImageSaver service."""

    def test_save_image_rgb(self, tmp_path: Path) -> None:
        """Test saving RGB image as PNG."""
        saver = ImageSaver()

        # Create RGB image
        pixel_data = np.zeros((100, 100, 3), dtype=np.uint8)
        pixel_data[:, :] = [255, 128, 64]

        image = ImageModel(
            width=100,
            height=100,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Save to temporary file
        output_path = tmp_path / "test_output.png"
        saver.save_image(image, str(output_path))

        # Verify file was created
        assert output_path.exists()

        # Verify file can be opened and has correct dimensions
        saved_image = PILImage.open(output_path)
        assert saved_image.size == (100, 100)
        assert saved_image.mode == "RGB"

    def test_save_image_rgba(self, tmp_path: Path) -> None:
        """Test saving RGBA image as PNG with alpha channel preservation."""
        saver = ImageSaver()

        # Create RGBA image
        pixel_data = np.zeros((50, 50, 4), dtype=np.uint8)
        pixel_data[:, :, :3] = [255, 0, 0]  # Red
        pixel_data[:, :, 3] = 128  # Alpha

        image = ImageModel(
            width=50,
            height=50,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        # Save to temporary file
        output_path = tmp_path / "test_rgba_output.png"
        saver.save_image(image, str(output_path))

        # Verify file was created
        assert output_path.exists()

        # Verify file can be opened and has alpha channel
        saved_image = PILImage.open(output_path)
        assert saved_image.size == (50, 50)
        assert saved_image.mode == "RGBA"

    def test_save_image_preserves_colors(self, tmp_path: Path) -> None:
        """Test that saved image preserves pixel colors correctly."""
        saver = ImageSaver()

        # Create image with specific colors
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[0:5, 0:5] = [255, 0, 0]  # Red
        pixel_data[0:5, 5:10] = [0, 255, 0]  # Green
        pixel_data[5:10, 0:5] = [0, 0, 255]  # Blue
        pixel_data[5:10, 5:10] = [255, 255, 0]  # Yellow

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Save
        output_path = tmp_path / "test_colors.png"
        saver.save_image(image, str(output_path))

        # Load and verify colors
        saved_image = PILImage.open(output_path)
        saved_array = np.array(saved_image)

        # Check a few pixels
        assert tuple(saved_array[2, 2]) == (255, 0, 0)  # Red
        assert tuple(saved_array[2, 7]) == (0, 255, 0)  # Green
        assert tuple(saved_array[7, 2]) == (0, 0, 255)  # Blue
        assert tuple(saved_array[7, 7]) == (255, 255, 0)  # Yellow

    def test_save_image_invalid_path(self) -> None:
        """Test saving to invalid path raises error."""
        saver = ImageSaver()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Try to save to invalid path
        with pytest.raises(ImageSaveError) as exc_info:
            saver.save_image(image, "/nonexistent/directory/image.png")
        
        # Check that user_message contains "Invalid file path"
        assert "Invalid file path" in exc_info.value.user_message

    def test_save_image_none_image(self) -> None:
        """Test saving None image raises error."""
        saver = ImageSaver()

        with pytest.raises(ValueError, match="Image cannot be None"):
            saver.save_image(None, "/tmp/test.png")

    def test_save_image_auto_adds_png_extension(self, tmp_path: Path) -> None:
        """Test that .png extension is added if missing."""
        saver = ImageSaver()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Save without .png extension
        output_path = tmp_path / "test_output"
        saver.save_image(image, str(output_path))

        # Verify .png was added
        assert (tmp_path / "test_output.png").exists()

    def test_save_image_preserves_alpha_channel(self, tmp_path: Path) -> None:
        """Test that alpha channel is preserved in saved RGBA image."""
        saver = ImageSaver()

        # Create RGBA image with varying alpha
        pixel_data = np.zeros((20, 20, 4), dtype=np.uint8)
        pixel_data[:, :, :3] = [255, 255, 255]  # White
        pixel_data[0:10, :, 3] = 255  # Full alpha
        pixel_data[10:20, :, 3] = 128  # Half alpha

        image = ImageModel(
            width=20,
            height=20,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        # Save
        output_path = tmp_path / "test_alpha.png"
        saver.save_image(image, str(output_path))

        # Load and verify alpha
        saved_image = PILImage.open(output_path)
        saved_array = np.array(saved_image)

        # Check alpha values
        assert saved_array[5, 5, 3] == 255  # Full alpha
        assert saved_array[15, 15, 3] == 128  # Half alpha

    def test_save_image_handles_permission_error(self, tmp_path: Path) -> None:
        """Test that permission errors are handled gracefully."""
        saver = ImageSaver()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Try to save to a path that might have permission issues
        # On Unix systems, /root/ is typically not writable
        # We'll test with a path that should fail
        invalid_path = "/root/test_image.png"

        # This should raise an error with a user-friendly message
        with pytest.raises(ImageSaveError):
            saver.save_image(image, invalid_path)

