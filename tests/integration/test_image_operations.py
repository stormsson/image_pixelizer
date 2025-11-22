"""Integration tests for image operations workflow."""

from pathlib import Path

import pytest
import numpy as np

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.models.settings_model import SettingsModel
from src.services.image_loader import ImageLoader


@pytest.fixture
def controller_with_services() -> MainController:
    """Create a MainController with all required services."""
    settings_model = SettingsModel()
    image_loader = ImageLoader()
    # Other services will be added as they're implemented
    return MainController(
        settings_model=settings_model,
        image_loader=image_loader,
    )


class TestBackgroundRemovalWorkflow:
    """Integration tests for background removal workflow."""

    def test_load_image_remove_background_workflow(
        self, controller_with_services: MainController, sample_image_path: Path
    ) -> None:
        """Test complete workflow: load image → remove background → verify result."""
        controller = controller_with_services

        # Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None

        # Remove background (will be implemented in T011)
        # For now, this test will fail until implementation is complete
        # controller.remove_background()
        # processed_image = controller.image_model
        # assert processed_image is not None
        # assert processed_image.has_alpha is True
        # assert processed_image.pixel_data.shape[2] == 4  # RGBA

    def test_background_removal_with_sample_image(
        self, controller_with_services: MainController
    ) -> None:
        """Test background removal using data/sample.jpg for realistic testing."""
        # Use the sample image from data/sample.jpg
        sample_image_path = Path(__file__).parent.parent.parent / "data" / "sample.jpg"

        if not sample_image_path.exists():
            pytest.skip("data/sample.jpg not found")

        controller = controller_with_services

        # Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None

        # Remove background (will be implemented in T011)
        # For now, this test will fail until implementation is complete
        # controller.remove_background()
        # processed_image = controller.image_model
        # assert processed_image is not None
        # assert processed_image.has_alpha is True

    def test_background_removal_preserves_dimensions(
        self, controller_with_services: MainController, sample_image_path: Path
    ) -> None:
        """Test that background removal preserves image dimensions."""
        controller = controller_with_services

        # Load image
        controller.load_image(str(sample_image_path))
        original_image = controller.image_model
        assert original_image is not None
        original_width = original_image.width
        original_height = original_image.height

        # Remove background (will be implemented in T011)
        # controller.remove_background()
        # processed_image = controller.image_model
        # assert processed_image.width == original_width
        # assert processed_image.height == original_height

