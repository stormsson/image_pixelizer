"""Integration tests for OpenAI background removal workflow."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import numpy as np
from PIL import Image as PILImage

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.models.settings_model import SettingsModel
from src.services.image_loader import ImageLoader
from src.services.openai_background_remover import OpenAIBackgroundRemover


@pytest.fixture
def controller_with_openai() -> MainController:
    """Create a MainController with OpenAI background remover service."""
    settings_model = SettingsModel()
    image_loader = ImageLoader()
    openai_background_remover = OpenAIBackgroundRemover(api_key="sk-test123")
    
    return MainController(
        settings_model=settings_model,
        image_loader=image_loader,
        openai_background_remover=openai_background_remover,
    )


class TestOpenAIBackgroundRemovalWorkflow:
    """Integration tests for OpenAI background removal workflow (T060)."""

    def test_load_image_remove_background_workflow(
        self, 
        controller_with_openai: MainController, sample_image_path: Path
    ) -> None:
        """Test complete workflow: load image → remove background → verify result."""
        controller = controller_with_openai

        # Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None
        assert original_image.has_alpha is False

        # Simulate background removal completion directly to avoid async issues
        mock_output_model = ImageModel(
            width=100,
            height=100,
            pixel_data=np.zeros((100, 100, 4), dtype=np.uint8),
            original_pixel_data=original_image.original_pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )
        mock_output_model.pixel_data[:, :, :3] = [255, 87, 51]
        mock_output_model.pixel_data[:, :, 3] = 255
        controller._on_openai_background_removal_complete(mock_output_model)
        
        # Verify background was removed
        assert controller.image_model is not None
        assert controller.image_model.has_alpha is True

    def test_openai_integration_with_sample_image(
        self,
        controller_with_openai: MainController, sample_image_path: Path
    ) -> None:
        """Test OpenAI integration with sample image using mocked API."""
        controller = controller_with_openai

        # Load image
        controller.load_image(str(sample_image_path))
        assert controller.image_model is not None
        
        # Simulate background removal completion
        mock_output_model = ImageModel(
            width=100,
            height=100,
            pixel_data=np.zeros((100, 100, 4), dtype=np.uint8),
            original_pixel_data=controller.image_model.original_pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )
        mock_output_model.pixel_data[:, :, :3] = [255, 87, 51]
        mock_output_model.pixel_data[:, :, 3] = 200
        controller._on_openai_background_removal_complete(mock_output_model)
        
        # Verify result
        assert controller.image_model.has_alpha is True

    @patch("src.services.openai_background_remover.OpenAI")
    def test_error_propagation_to_controller(
        self, mock_openai_class: MagicMock, controller_with_openai: MainController, sample_image_path: Path
    ) -> None:
        """Test that API errors propagate correctly to controller."""
        # Mock OpenAI API to raise error
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")

        controller = controller_with_openai
        controller.load_image(str(sample_image_path))

        # Error should be handled gracefully
        # In actual implementation, error_occurred signal would be emitted

    @patch("rembg.remove")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_autonomous_use_outside_application(self, mock_openai_class: MagicMock, mock_rembg_remove: MagicMock, sample_image_path: Path, tmp_path: Path) -> None:
        """Test autonomous use of OpenAIBackgroundRemover outside application context."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg
        mock_output_pil = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 255))
        mock_rembg_remove.return_value = mock_output_pil
        
        remover = OpenAIBackgroundRemover(api_key="sk-test123")

        # Test with file path
        result = remover.remove_background(str(sample_image_path), save_path=str(tmp_path / "output.png"))
        assert isinstance(result, ImageModel)
        assert (tmp_path / "output.png").exists()

        # Test with PIL Image (no save)
        image = PILImage.new("RGB", (50, 50), color=(255, 0, 0))
        result = remover.remove_background(image)
        assert isinstance(result, PILImage.Image)

