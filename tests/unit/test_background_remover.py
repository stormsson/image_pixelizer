"""Unit tests for BackgroundRemovalError exception and BackgroundRemover service."""

from unittest.mock import Mock, patch, MagicMock

import pytest
import numpy as np
from PIL import Image as PILImage

from src.models.image_model import ImageModel
from src.services import BackgroundRemovalError, ImageProcessingError


class TestBackgroundRemovalError:
    """Tests for BackgroundRemovalError exception class."""

    def test_inherits_from_image_processing_error(self) -> None:
        """Test that BackgroundRemovalError inherits from ImageProcessingError."""
        error = BackgroundRemovalError("Test error")
        assert isinstance(error, ImageProcessingError)
        assert isinstance(error, Exception)

    def test_exception_creation_with_message(self) -> None:
        """Test creating BackgroundRemovalError with technical message."""
        error = BackgroundRemovalError("Technical error message")

        assert str(error) == "Technical error message"
        assert error.user_message == "Technical error message"

    def test_exception_creation_with_user_message(self) -> None:
        """Test creating BackgroundRemovalError with both technical and user messages."""
        error = BackgroundRemovalError(
            "Technical error: rembg processing failed",
            user_message="Failed to remove background. Please try again or use a different image.",
        )

        assert str(error) == "Technical error: rembg processing failed"
        assert error.user_message == "Failed to remove background. Please try again or use a different image."

    def test_exception_creation_user_message_only(self) -> None:
        """Test creating BackgroundRemovalError with only user message (uses as technical too)."""
        error = BackgroundRemovalError(
            "Failed to remove background. Please try again or use a different image."
        )

        assert str(error) == "Failed to remove background. Please try again or use a different image."
        assert error.user_message == "Failed to remove background. Please try again or use a different image."

    def test_exception_can_be_raised(self) -> None:
        """Test that BackgroundRemovalError can be raised and caught."""
        with pytest.raises(BackgroundRemovalError) as exc_info:
            raise BackgroundRemovalError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_exception_can_be_caught_as_base_class(self) -> None:
        """Test that BackgroundRemovalError can be caught as ImageProcessingError."""
        with pytest.raises(ImageProcessingError) as exc_info:
            raise BackgroundRemovalError("Test error")

        assert isinstance(exc_info.value, BackgroundRemovalError)

    def test_user_message_attribute(self) -> None:
        """Test that user_message attribute is accessible."""
        error = BackgroundRemovalError(
            "Technical: rembg failed",
            user_message="User-friendly message"
        )

        assert hasattr(error, "user_message")
        assert error.user_message == "User-friendly message"

    def test_exception_with_empty_message(self) -> None:
        """Test creating BackgroundRemovalError with empty message."""
        error = BackgroundRemovalError("")

        assert str(error) == ""
        assert error.user_message == ""


class TestBackgroundRemover:
    """Tests for BackgroundRemover service class."""

    @patch("src.services.background_remover.rembg")
    def test_remove_background_rgb_to_rgba(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test removing background from RGB image produces RGBA output."""
        from src.services.background_remover import BackgroundRemover

        # Mock rembg.remove() to return RGBA PIL Image
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg.remove.return_value = mock_output

        remover = BackgroundRemover()
        result = remover.remove_background(sample_image_model)

        assert isinstance(result, ImageModel)
        assert result.width == sample_image_model.width
        assert result.height == sample_image_model.height
        assert result.has_alpha is True
        assert result.pixel_data.shape[2] == 4  # RGBA

    @patch("src.services.background_remover.rembg")
    def test_remove_background_rgba_to_rgba(self, mock_rembg: Mock, sample_rgba_image_model: ImageModel) -> None:
        """Test removing background from RGBA image produces RGBA output."""
        from src.services.background_remover import BackgroundRemover

        # Mock rembg.remove() to return RGBA PIL Image
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 128))
        mock_rembg.remove.return_value = mock_output

        remover = BackgroundRemover()
        result = remover.remove_background(sample_rgba_image_model)

        assert isinstance(result, ImageModel)
        assert result.width == sample_rgba_image_model.width
        assert result.height == sample_rgba_image_model.height
        assert result.has_alpha is True
        assert result.pixel_data.shape[2] == 4  # RGBA

    @patch("src.services.background_remover.rembg")
    def test_remove_background_preserves_dimensions(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that background removal preserves image dimensions."""
        from src.services.background_remover import BackgroundRemover

        # Mock rembg.remove() to return RGBA PIL Image with same dimensions
        mock_output = PILImage.new("RGBA", (sample_image_model.width, sample_image_model.height))
        mock_rembg.remove.return_value = mock_output

        remover = BackgroundRemover()
        result = remover.remove_background(sample_image_model)

        assert result.width == sample_image_model.width
        assert result.height == sample_image_model.height

    @patch("src.services.background_remover.rembg")
    def test_remove_background_creates_alpha_channel(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that background removal always creates alpha channel."""
        from src.services.background_remover import BackgroundRemover

        # Mock rembg.remove() to return RGBA PIL Image
        mock_output = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg.remove.return_value = mock_output

        remover = BackgroundRemover()
        result = remover.remove_background(sample_image_model)

        assert result.has_alpha is True
        assert result.pixel_data.shape[2] == 4  # RGBA

    @patch("src.services.background_remover.rembg")
    def test_remove_background_rembg_integration(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that rembg.remove() is called with correct PIL Image."""
        from src.services.background_remover import BackgroundRemover

        # Mock rembg.remove() to return RGBA PIL Image
        mock_output = PILImage.new("RGBA", (100, 100))
        mock_rembg.remove.return_value = mock_output

        remover = BackgroundRemover()
        remover.remove_background(sample_image_model)

        # Verify rembg.remove() was called once
        assert mock_rembg.remove.call_count == 1
        # Verify it was called with a PIL Image
        call_args = mock_rembg.remove.call_args[0]
        assert isinstance(call_args[0], PILImage.Image)

    def test_remove_background_invalid_image_none(self) -> None:
        """Test that None image raises ValueError."""
        from src.services.background_remover import BackgroundRemover

        remover = BackgroundRemover()
        with pytest.raises(ValueError, match="Invalid image"):
            remover.remove_background(None)  # type: ignore

    @patch("src.services.background_remover.rembg")
    def test_remove_background_rembg_processing_error(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that rembg processing errors raise BackgroundRemovalError."""
        from src.services.background_remover import BackgroundRemover

        # Mock rembg.remove() to raise an exception
        mock_rembg.remove.side_effect = Exception("rembg processing failed")

        remover = BackgroundRemover()
        with pytest.raises(BackgroundRemovalError) as exc_info:
            remover.remove_background(sample_image_model)

        assert "Failed to remove background" in exc_info.value.user_message

    @patch("src.services.background_remover.rembg")
    def test_remove_background_with_different_sizes(self, mock_rembg: Mock) -> None:
        """Test background removal with various image sizes."""
        from src.services.background_remover import BackgroundRemover

        remover = BackgroundRemover()

        # Test small image (10x10)
        small_pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        small_image = ImageModel(
            width=10,
            height=10,
            pixel_data=small_pixel_data,
            original_pixel_data=small_pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )
        mock_output_small = PILImage.new("RGBA", (10, 10))
        mock_rembg.remove.return_value = mock_output_small

        result_small = remover.remove_background(small_image)
        assert result_small.width == 10
        assert result_small.height == 10

        # Test medium image (500x500)
        medium_pixel_data = np.zeros((500, 500, 3), dtype=np.uint8)
        medium_image = ImageModel(
            width=500,
            height=500,
            pixel_data=medium_pixel_data,
            original_pixel_data=medium_pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )
        mock_output_medium = PILImage.new("RGBA", (500, 500))
        mock_rembg.remove.return_value = mock_output_medium

        result_medium = remover.remove_background(medium_image)
        assert result_medium.width == 500
        assert result_medium.height == 500

    def test_rembg_import_error_handling(self) -> None:
        """Test that missing rembg import is handled gracefully."""
        # This test verifies the import error handling in the module
        # We'll test this by checking if the module can be imported
        # and if BackgroundRemover can be instantiated
        try:
            from src.services.background_remover import BackgroundRemover
            remover = BackgroundRemover()
            # If we get here, the import worked (rembg is installed)
            assert remover is not None
        except ImportError as e:
            # If rembg is not installed, we should get a clear error
            assert "rembg" in str(e).lower() or "Background removal requires rembg" in str(e)

    @patch("src.services.background_remover.rembg")
    def test_remove_background_with_sam_prompts(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test removing background with SAM point prompts."""
        from src.services.background_remover import BackgroundRemover

        # Mock new_session and remove
        mock_session = Mock()
        mock_rembg.new_session.return_value = mock_session
        mock_output = PILImage.new("RGBA", (100, 100))
        mock_rembg.remove.return_value = mock_output

        # Create SAM prompts: keep point and remove point
        prompts = [
            {"type": "point", "data": [50, 50], "label": 1},  # Keep point
            {"type": "point", "data": [10, 10], "label": 0},  # Remove point
        ]

        remover = BackgroundRemover(model="sam")
        result = remover.remove_background(sample_image_model, prompts=prompts)

        # Verify session was created
        mock_rembg.new_session.assert_called_once_with("sam")
        # Verify remove was called with session and prompts
        mock_rembg.remove.assert_called_once()
        call_kwargs = mock_rembg.remove.call_args[1]
        assert call_kwargs["session"] == mock_session
        assert "extra" in call_kwargs
        assert call_kwargs["extra"]["sam_prompt"] == prompts
        # Verify result
        assert isinstance(result, ImageModel)
        assert result.has_alpha is True

    @patch("src.services.background_remover.rembg")
    def test_remove_background_sam_model_initialization(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that SAM model session is created on first use."""
        from src.services.background_remover import BackgroundRemover

        mock_session = Mock()
        mock_rembg.new_session.return_value = mock_session
        mock_output = PILImage.new("RGBA", (100, 100))
        mock_rembg.remove.return_value = mock_output

        remover = BackgroundRemover(model="sam")
        remover.remove_background(sample_image_model)

        # Verify session was created
        mock_rembg.new_session.assert_called_once_with("sam")
        # Verify remove was called with session
        assert mock_rembg.remove.call_args[1]["session"] == mock_session

    @patch("src.services.background_remover.rembg")
    def test_remove_background_sam_prompt_format_conversion(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that prompts are correctly formatted for SAM."""
        from src.services.background_remover import BackgroundRemover

        mock_session = Mock()
        mock_rembg.new_session.return_value = mock_session
        mock_output = PILImage.new("RGBA", (100, 100))
        mock_rembg.remove.return_value = mock_output

        # Test point prompts with keep (label=1) and remove (label=0)
        prompts = [
            {"type": "point", "data": [25, 30], "label": 1},
            {"type": "point", "data": [75, 80], "label": 0},
        ]

        remover = BackgroundRemover(model="sam")
        remover.remove_background(sample_image_model, prompts=prompts)

        # Verify prompts were passed correctly
        call_kwargs = mock_rembg.remove.call_args[1]
        assert call_kwargs["extra"]["sam_prompt"] == prompts

    @patch("src.services.background_remover.rembg")
    def test_remove_background_sam_model_initialization_error(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that SAM model initialization errors raise BackgroundRemovalError."""
        from src.services.background_remover import BackgroundRemover

        # Mock new_session to raise an exception
        mock_rembg.new_session.side_effect = Exception("Model download failed")

        remover = BackgroundRemover(model="sam")
        with pytest.raises(BackgroundRemovalError) as exc_info:
            remover.remove_background(sample_image_model)

        assert "Failed to initialize sam model" in exc_info.value.user_message

    @patch("src.services.background_remover.rembg")
    def test_remove_background_sam_prompts_ignored_for_u2net(self, mock_rembg: Mock, sample_image_model: ImageModel) -> None:
        """Test that prompts are ignored when using u2net model."""
        from src.services.background_remover import BackgroundRemover

        mock_output = PILImage.new("RGBA", (100, 100))
        mock_rembg.remove.return_value = mock_output

        prompts = [{"type": "point", "data": [50, 50], "label": 1}]

        remover = BackgroundRemover(model="u2net")
        result = remover.remove_background(sample_image_model, prompts=prompts)

        # Verify remove was called without session or extra
        call_kwargs = mock_rembg.remove.call_args[1] if mock_rembg.remove.call_args[1] else {}
        assert "session" not in call_kwargs
        assert "extra" not in call_kwargs
        # Verify result still works
        assert isinstance(result, ImageModel)

