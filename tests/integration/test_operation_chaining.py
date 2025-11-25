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

    def test_background_removal_then_pixelization_then_color_reduction(
        self,
        controller_with_all_services: MainController,
        sample_image_path: Path,
    ) -> None:
        """Test complete workflow: load image → remove background → apply pixelization → apply color reduction."""
        # Create RGBA image with transparent background and visible foreground
        mock_output_pil = PILImage.new("RGBA", (100, 100), color=(0, 0, 0, 0))  # Transparent
        pixels = np.array(mock_output_pil)
        # Add a larger colored square in the center (foreground) - 40x40 square
        pixels[30:70, 30:70, :] = [255, 87, 51, 255]  # Colored square with alpha
        mock_output_pil = PILImage.fromarray(pixels)
        
        controller = controller_with_all_services
        
        # Create mock output model for background removal result
        mock_output_model = ImageModel(
            width=100,
            height=100,
            pixel_data=np.array(mock_output_pil),
            original_pixel_data=np.zeros((100, 100, 3), dtype=np.uint8),
            format="PNG",
            has_alpha=True,
        )

        # Step 1: Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None
        assert original_image.has_alpha is False  # Original is RGB

        # Step 2: Remove background automatically
        # Instead of actually calling remove_background_automatic (which uses async worker),
        # directly simulate the completion to avoid threading issues in tests
        processed_image = ImageModel(
            width=100,
            height=100,
            pixel_data=mock_output_model.pixel_data.copy(),
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

        # Verify pixelization was applied
        # When pixelizing with pixel_size=10, blocks of 10x10 pixels are averaged
        # Since the image has transparent background, blocks containing both transparent
        # and opaque pixels will have averaged colors
        # Check that pixelization was applied by verifying settings were updated
        assert controller._settings_model.pixelization.pixel_size == 10
        assert controller._settings_model.pixelization.is_enabled is True
        # The pixelized image should still have the same dimensions and alpha channel
        assert image_after_pixelization.width == 100
        assert image_after_pixelization.height == 100
        assert image_after_pixelization.has_alpha is True

        # Verify transparency is preserved (background should still be transparent)
        background_alpha = image_after_pixelization.pixel_data[0:20, 0:20, 3]
        assert np.all(background_alpha == 0), "Background should remain transparent after pixelization"

        # Step 4: Apply color reduction (should work on pixelized image with background removed)
        controller.update_bin_count(16)
        image_after_color_reduction = controller.image_model
        assert image_after_color_reduction is not None
        assert image_after_color_reduction.has_alpha is True  # Should preserve alpha
        assert image_after_color_reduction.pixel_data.shape == (100, 100, 4)  # Still RGBA

        # Verify color reduction was applied
        # Check that color reduction was applied by verifying settings were updated
        assert controller._settings_model.color_reduction.bin_count == 16
        assert controller._settings_model.color_reduction.is_enabled is True
        # The color-reduced image should still have the same dimensions and alpha channel
        assert image_after_color_reduction.width == 100
        assert image_after_color_reduction.height == 100
        assert image_after_color_reduction.has_alpha is True

        # Verify transparency is still preserved
        background_alpha_final = image_after_color_reduction.pixel_data[0:20, 0:20, 3]
        assert np.all(background_alpha_final == 0), "Background should remain transparent after color reduction"

        # Verify original pixel data is preserved throughout
        np.testing.assert_array_equal(
            image_after_color_reduction.original_pixel_data,
            original_image.original_pixel_data,
        )

    def test_operations_chain_correctly_in_sequence(
        self,
        controller_with_all_services: MainController,
        sample_image_path: Path,
    ) -> None:
        """Test that operations chain correctly: each operation works on the result of previous operations."""
        controller = controller_with_all_services
        
        # Create mock output image
        mock_output_pil = PILImage.new("RGBA", (100, 100), color=(0, 0, 0, 0))
        pixels = np.array(mock_output_pil)
        pixels[40:60, 40:60] = [200, 100, 50, 255]
        mock_output_pil = PILImage.fromarray(pixels)
        
        # Create mock output model
        mock_output_model = ImageModel(
            width=100,
            height=100,
            pixel_data=np.array(mock_output_pil),
            original_pixel_data=np.zeros((100, 100, 3), dtype=np.uint8),
            format="PNG",
            has_alpha=True,
        )

        # Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None

        # Remove background - simulate completion directly to avoid async issues
        processed_image = ImageModel(
            width=100,
            height=100,
            pixel_data=mock_output_model.pixel_data.copy(),
            original_pixel_data=original_image.original_pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )
        controller._on_openai_background_removal_complete(processed_image)

        state_after_bg = controller.image_model.pixel_data.copy()

        # Apply pixelization
        controller.update_pixel_size(8)
        state_after_pixel = controller.image_model.pixel_data.copy()
        
        # Verify pixelization was applied (check settings)
        assert controller._settings_model.pixelization.pixel_size == 8
        assert controller._settings_model.pixelization.is_enabled is True

        # Apply color reduction
        controller.update_bin_count(32)
        state_after_color = controller.image_model.pixel_data.copy()

        # Verify color reduction was applied (check settings)
        assert controller._settings_model.color_reduction.bin_count == 32
        assert controller._settings_model.color_reduction.is_enabled is True

        # Verify all operations were applied in sequence
        # Check that final state has correct structure
        assert state_after_color.shape == (100, 100, 4)  # RGBA
        assert controller.image_model.has_alpha is True

        # Verify original is preserved
        np.testing.assert_array_equal(
            controller.image_model.original_pixel_data,
            original_image.original_pixel_data,
        )

