"""Integration tests for operation chaining workflow (FR-017)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import numpy as np
from PIL import Image as PILImage

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.models.settings_model import SettingsModel
from src.services.color_reducer import ColorReducer
from src.services.image_loader import ImageLoader
from src.services.openai_background_remover import OpenAIBackgroundRemover
from src.services.pixelizer import Pixelizer


@pytest.fixture
def controller_with_all_services() -> MainController:
    """Create a MainController with all services for operation chaining tests."""
    settings_model = SettingsModel()
    image_loader = ImageLoader()
    pixelizer = Pixelizer()
    color_reducer = ColorReducer()
    openai_background_remover = OpenAIBackgroundRemover(api_key="sk-test123")
    
    return MainController(
        settings_model=settings_model,
        image_loader=image_loader,
        pixelizer=pixelizer,
        color_reducer=color_reducer,
        openai_background_remover=openai_background_remover,
    )


class TestOperationChainingWorkflow:
    """Integration tests for operation chaining: background removal → pixelization → color reduction."""

    @patch("src.services.openai_background_remover.rembg")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_background_removal_then_pixelization_then_color_reduction(
        self,
        mock_openai_class: MagicMock,
        mock_rembg: MagicMock,
        controller_with_all_services: MainController,
        sample_image_path: Path,
    ) -> None:
        """Test complete workflow: load image → remove background → apply pixelization → apply color reduction."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Background removal analysis"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg to return image with transparent background
        # Create RGBA image with transparent background
        mock_output = PILImage.new("RGBA", (100, 100), color=(0, 0, 0, 0))  # Transparent
        # Add a colored square in the center (foreground)
        pixels = np.array(mock_output)
        pixels[30:70, 30:70] = [255, 87, 51, 255]  # Colored square with alpha
        mock_output = PILImage.fromarray(pixels)
        mock_rembg.remove.return_value = mock_output

        controller = controller_with_all_services

        # Step 1: Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None
        assert original_image.has_alpha is False  # Original is RGB

        # Step 2: Remove background automatically
        controller.remove_background_automatic()
        
        # Wait for async processing (simulate by checking worker result)
        # In real scenario, this would be handled via signals
        # For test, we'll manually trigger the completion
        if hasattr(controller, "_openai_background_removal_worker"):
            # Simulate worker completion
            processed_image = ImageModel(
                width=100,
                height=100,
                pixel_data=np.array(mock_output),
                original_pixel_data=original_image.original_pixel_data.copy(),
                format="PNG",
                has_alpha=True,
            )
            controller._on_openai_background_removal_complete(processed_image)

        # Verify background was removed
        image_after_bg_removal = controller.image_model
        assert image_after_bg_removal is not None
        assert image_after_bg_removal.has_alpha is True  # Now has alpha channel
        assert image_after_bg_removal.pixel_data.shape == (100, 100, 4)  # RGBA

        # Store pixel data after background removal for comparison
        pixel_data_after_bg = image_after_bg_removal.pixel_data.copy()

        # Step 3: Apply pixelization (should work on current state with background removed)
        controller.update_pixel_size(10)
        image_after_pixelization = controller.image_model
        assert image_after_pixelization is not None
        assert image_after_pixelization.has_alpha is True  # Should preserve alpha
        assert image_after_pixelization.pixel_data.shape == (100, 100, 4)  # Still RGBA

        # Verify pixelization was applied (pixel blocks should be visible)
        # The pixelized image should be different from the background-removed image
        assert not np.array_equal(
            image_after_pixelization.pixel_data,
            pixel_data_after_bg,
        )

        # Verify transparency is preserved (background should still be transparent)
        background_alpha = image_after_pixelization.pixel_data[0:20, 0:20, 3]
        assert np.all(background_alpha == 0), "Background should remain transparent after pixelization"

        # Step 4: Apply color reduction (should work on pixelized image with background removed)
        controller.update_sensitivity(0.5)
        image_after_color_reduction = controller.image_model
        assert image_after_color_reduction is not None
        assert image_after_color_reduction.has_alpha is True  # Should preserve alpha
        assert image_after_color_reduction.pixel_data.shape == (100, 100, 4)  # Still RGBA

        # Verify color reduction was applied
        # The color-reduced image should be different from the pixelized image
        assert not np.array_equal(
            image_after_color_reduction.pixel_data,
            image_after_pixelization.pixel_data,
        )

        # Verify transparency is still preserved
        background_alpha_final = image_after_color_reduction.pixel_data[0:20, 0:20, 3]
        assert np.all(background_alpha_final == 0), "Background should remain transparent after color reduction"

        # Verify original pixel data is preserved throughout
        np.testing.assert_array_equal(
            image_after_color_reduction.original_pixel_data,
            original_image.original_pixel_data,
        )

    @patch("src.services.openai_background_remover.rembg")
    @patch("src.services.openai_background_remover.OpenAI")
    def test_operations_chain_correctly_in_sequence(
        self,
        mock_openai_class: MagicMock,
        mock_rembg: MagicMock,
        controller_with_all_services: MainController,
        sample_image_path: Path,
    ) -> None:
        """Test that operations chain correctly: each operation works on the result of previous operations."""
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Background removal"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock rembg
        mock_output = PILImage.new("RGBA", (100, 100), color=(0, 0, 0, 0))
        pixels = np.array(mock_output)
        pixels[40:60, 40:60] = [200, 100, 50, 255]
        mock_output = PILImage.fromarray(pixels)
        mock_rembg.remove.return_value = mock_output

        controller = controller_with_all_services

        # Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None

        # Remove background
        controller.remove_background_automatic()
        if hasattr(controller, "_openai_background_removal_worker"):
            processed_image = ImageModel(
                width=100,
                height=100,
                pixel_data=np.array(mock_output),
                original_pixel_data=original_image.original_pixel_data.copy(),
                format="PNG",
                has_alpha=True,
            )
            controller._on_openai_background_removal_complete(processed_image)

        state_after_bg = controller.image_model.pixel_data.copy()

        # Apply pixelization
        controller.update_pixel_size(8)
        state_after_pixel = controller.image_model.pixel_data.copy()
        
        # Verify pixelization changed the image
        assert not np.array_equal(state_after_pixel, state_after_bg)

        # Apply color reduction
        controller.update_sensitivity(0.6)
        state_after_color = controller.image_model.pixel_data.copy()

        # Verify color reduction changed the image
        assert not np.array_equal(state_after_color, state_after_pixel)

        # Verify all operations were applied in sequence
        # Final state should be different from all intermediate states
        assert not np.array_equal(state_after_color, state_after_bg)
        assert not np.array_equal(state_after_color, state_after_pixel)
        assert not np.array_equal(state_after_color, original_image.pixel_data)

        # Verify original is preserved
        np.testing.assert_array_equal(
            controller.image_model.original_pixel_data,
            original_image.original_pixel_data,
        )

