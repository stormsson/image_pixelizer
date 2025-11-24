"""Integration tests for levels adjustment workflow."""

import numpy as np
import pytest

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.models.settings_model import SettingsModel
from src.services.color_reducer import ColorReducer
from src.services.image_loader import ImageLoader
from src.services.image_saver import ImageSaver
from src.services.levels_adjuster import LevelsAdjuster
from src.services.pixelizer import Pixelizer
from src.views.levels_window import LevelsWindow
from tests.conftest import (
    color_reducer,
    image_loader,
    image_saver,
    pixelizer,
    sample_image_path,
    settings_model,
)


@pytest.fixture
def levels_adjuster() -> LevelsAdjuster:
    """Create a LevelsAdjuster instance for testing."""
    return LevelsAdjuster()


@pytest.fixture
def controller_with_levels(
    settings_model: SettingsModel,
    image_loader: ImageLoader,
    image_saver: ImageSaver,
    pixelizer: Pixelizer,
    color_reducer: ColorReducer,
    levels_adjuster: LevelsAdjuster,
) -> MainController:
    """Create a MainController instance with levels adjuster."""
    return MainController(
        settings_model=settings_model,
        image_loader=image_loader,
        image_saver=image_saver,
        pixelizer=pixelizer,
        color_reducer=color_reducer,
        levels_adjuster=levels_adjuster,
    )


class TestLevelsIntegration:
    """Integration tests for end-to-end levels workflow (T060)."""

    def test_load_image_open_levels_window_adjust_sliders(
        self, controller_with_levels: MainController, sample_image_path
    ) -> None:
        """Test complete workflow: load image → open levels window → adjust sliders → verify image updated."""
        # Load image
        controller_with_levels.load_image(str(sample_image_path))
        assert controller_with_levels.image_model is not None

        # Open levels window
        window = LevelsWindow(controller_with_levels)
        assert window is not None

        # Verify histogram is displayed
        from src.views.levels_window import HistogramWidget
        histogram_widget = window.findChild(HistogramWidget)
        assert histogram_widget is not None

        # Adjust sliders (simulated)
        # This would normally be done via UI interaction
        # For integration test, we'll call the service directly
        original_image = controller_with_levels.image_model
        levels_adjuster = LevelsAdjuster()
        adjusted_image = levels_adjuster.apply_levels(original_image, darks_cutoff=5.0, lights_cutoff=10.0)

        # Verify image was adjusted
        assert adjusted_image is not None
        assert adjusted_image.width == original_image.width
        assert adjusted_image.height == original_image.height

    def test_verify_operation_history(self, controller_with_levels: MainController, sample_image_path) -> None:
        """Test that levels adjustment is tracked in operation history."""
        # Load image
        controller_with_levels.load_image(str(sample_image_path))
        assert controller_with_levels.image_model is not None

        # Apply levels adjustment
        original_image = controller_with_levels.image_model
        levels_adjuster = LevelsAdjuster()
        adjusted_image = levels_adjuster.apply_levels(original_image, darks_cutoff=5.0, lights_cutoff=10.0)
        controller_with_levels.apply_levels_adjustment(adjusted_image)

        # Verify operation history
        assert controller_with_levels.can_undo() is True

    def test_snapshot_behavior_with_other_operations(
        self, controller_with_levels: MainController, sample_image_path, qtbot
    ) -> None:
        """Test snapshot behavior when other operations are applied (T064)."""
        # Load image
        controller_with_levels.load_image(str(sample_image_path))
        assert controller_with_levels.image_model is not None

        # Open levels window - snapshot should be captured
        window = LevelsWindow(controller_with_levels)
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)
        
        assert window._base_image_for_levels is not None
        initial_snapshot = window._base_image_for_levels.pixel_data.copy()

        # Apply levels adjustment
        levels_adjuster = LevelsAdjuster()
        adjusted_image = levels_adjuster.apply_levels(
            window._base_image_for_levels, darks_cutoff=5.0, lights_cutoff=10.0
        )
        controller_with_levels.apply_levels_adjustment(adjusted_image)

        # Verify snapshot is still based on original state (not the adjusted image)
        assert window._base_image_for_levels is not None
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            initial_snapshot
        )

        # Apply another operation (e.g., pixelization)
        if controller_with_levels._pixelizer:
            pixelized_image = controller_with_levels._pixelizer.pixelize(
                controller_with_levels.image_model, pixel_size=5
            )
            controller_with_levels._image_model = pixelized_image
            controller_with_levels.image_updated.emit(pixelized_image)

        # Verify snapshot is still based on original state before levels window opened
        assert window._base_image_for_levels is not None
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            initial_snapshot
        )

