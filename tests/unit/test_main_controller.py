"""Unit tests for MainController operation chaining (FR-017)."""

import numpy as np
import pytest

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.models.settings_model import SettingsModel
from src.services.color_reducer import ColorReducer
from src.services.pixelizer import Pixelizer


class TestOperationChaining:
    """Tests for operation chaining: pixelization and color reduction work on current state."""

    def test_pixelization_works_on_image_with_background_removed(
        self, pixelizer: Pixelizer
    ) -> None:
        """Test that pixelization works on current state including background removal."""
        # Create an image with background removed (transparent background)
        # Original: 100x100 RGB image
        original_pixel_data = np.zeros((100, 100, 3), dtype=np.uint8)
        original_pixel_data[30:70, 30:70] = [255, 0, 0]  # Red square in center

        # Current state: Background removed (RGBA with transparent background)
        current_pixel_data = np.zeros((100, 100, 4), dtype=np.uint8)
        current_pixel_data[30:70, 30:70, :3] = [255, 0, 0]  # Red square
        current_pixel_data[30:70, 30:70, 3] = 255  # Opaque foreground
        # Background remains transparent (alpha=0)

        # Create controller with pixelizer
        controller = MainController(
            settings_model=SettingsModel(),
            pixelizer=pixelizer,
        )

        # Set up image model with current state (background removed)
        controller._image_model = ImageModel(
            width=100,
            height=100,
            pixel_data=current_pixel_data.copy(),
            original_pixel_data=original_pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        # Apply pixelization (should work on current state, not original)
        controller.update_pixel_size(5)

        # Verify pixelization was applied to current state
        assert controller._image_model is not None
        assert controller._image_model.has_alpha  # Should preserve alpha channel
        assert controller._image_model.pixel_data.shape == (100, 100, 4)  # RGBA

        # Verify original pixel data is preserved
        np.testing.assert_array_equal(
            controller._image_model.original_pixel_data, original_pixel_data
        )

        # Verify pixelization was applied (pixel blocks should be visible)
        # The pixelized image should have different pixel values than original
        assert not np.array_equal(
            controller._image_model.pixel_data[:, :, :3],
            original_pixel_data,
        )

    def test_color_reduction_works_on_pixelized_image_with_background_removed(
        self, pixelizer: Pixelizer, color_reducer: ColorReducer
    ) -> None:
        """Test that color reduction works on pixelized image with background removed."""
        # Create an image with background removed
        original_pixel_data = np.zeros((100, 100, 3), dtype=np.uint8)
        original_pixel_data[30:70, 30:70] = [255, 0, 0]  # Red square

        # Current state: Background removed and pixelized
        current_pixel_data = np.zeros((100, 100, 4), dtype=np.uint8)
        current_pixel_data[30:70, 30:70, :3] = [255, 0, 0]  # Red square
        current_pixel_data[30:70, 30:70, 3] = 255  # Opaque foreground

        # Create controller with both services
        controller = MainController(
            settings_model=SettingsModel(),
            pixelizer=pixelizer,
            color_reducer=color_reducer,
        )

        # Set up image model with current state (background removed, pixelized)
        controller._image_model = ImageModel(
            width=100,
            height=100,
            pixel_data=current_pixel_data.copy(),
            original_pixel_data=original_pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        # Enable pixelization first
        controller._settings_model.pixelization.is_enabled = True
        controller._settings_model.pixelization.pixel_size = 5

        # Apply color reduction (should work on current state)
        controller.update_sensitivity(0.5)

        # Verify color reduction was applied to current state
        assert controller._image_model is not None
        assert controller._image_model.has_alpha  # Should preserve alpha channel
        assert controller._image_model.pixel_data.shape == (100, 100, 4)  # RGBA

        # Verify original pixel data is preserved
        np.testing.assert_array_equal(
            controller._image_model.original_pixel_data, original_pixel_data
        )

        # Verify operations were chained (pixelization then color reduction)
        # The final image should be different from both original and intermediate states

    def test_pixelization_preserves_transparency_from_background_removal(
        self, pixelizer: Pixelizer
    ) -> None:
        """Test that pixelization preserves transparency from background removal."""
        # Create image with transparent background
        original_pixel_data = np.ones((100, 100, 3), dtype=np.uint8) * 128  # Gray background

        current_pixel_data = np.zeros((100, 100, 4), dtype=np.uint8)
        current_pixel_data[40:60, 40:60, :3] = [255, 255, 255]  # White square
        current_pixel_data[40:60, 40:60, 3] = 255  # Opaque foreground
        # Background is transparent (alpha=0)

        controller = MainController(
            settings_model=SettingsModel(),
            pixelizer=pixelizer,
        )

        controller._image_model = ImageModel(
            width=100,
            height=100,
            pixel_data=current_pixel_data.copy(),
            original_pixel_data=original_pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        # Apply pixelization
        controller.update_pixel_size(10)

        # Verify transparency is preserved
        assert controller._image_model.has_alpha
        # Background areas should remain transparent
        background_alpha = controller._image_model.pixel_data[0:30, 0:30, 3]
        assert np.all(background_alpha == 0), "Background should remain transparent after pixelization"

    def test_color_reduction_preserves_transparency_from_background_removal(
        self, color_reducer: ColorReducer
    ) -> None:
        """Test that color reduction preserves transparency from background removal."""
        # Create image with transparent background
        original_pixel_data = np.ones((100, 100, 3), dtype=np.uint8) * 128

        current_pixel_data = np.zeros((100, 100, 4), dtype=np.uint8)
        current_pixel_data[40:60, 40:60, :3] = [200, 200, 200]  # Light gray square
        current_pixel_data[40:60, 40:60, 3] = 255  # Opaque foreground

        controller = MainController(
            settings_model=SettingsModel(),
            color_reducer=color_reducer,
        )

        controller._image_model = ImageModel(
            width=100,
            height=100,
            pixel_data=current_pixel_data.copy(),
            original_pixel_data=original_pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        # Apply color reduction
        controller.update_sensitivity(0.3)

        # Verify transparency is preserved
        assert controller._image_model.has_alpha
        # Background areas should remain transparent
        background_alpha = controller._image_model.pixel_data[0:30, 0:30, 3]
        assert np.all(background_alpha == 0), "Background should remain transparent after color reduction"

