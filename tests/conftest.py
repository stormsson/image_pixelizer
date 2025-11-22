"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import pytest
from PIL import Image as PILImage
from PySide6.QtWidgets import QApplication

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.models.settings_model import SettingsModel
from src.services.color_reducer import ColorReducer
from src.services.image_loader import ImageLoader
from src.services.image_saver import ImageSaver
from src.services.pixelizer import Pixelizer


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Create QApplication instance for GUI tests (session-scoped)."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    """Create a temporary sample image file for testing.

    Returns:
        Path to a 100x100 RGB PNG image file.
    """
    # Create a simple 100x100 RGB image
    image = PILImage.new("RGB", (100, 100), color=(255, 87, 51))
    image_path = tmp_path / "test_image.png"
    image.save(image_path)
    return image_path


@pytest.fixture
def sample_rgba_image_path(tmp_path: Path) -> Path:
    """Create a temporary RGBA image file for testing.

    Returns:
        Path to a 100x100 RGBA PNG image file with transparency.
    """
    # Create a simple 100x100 RGBA image
    image = PILImage.new("RGBA", (100, 100), color=(255, 87, 51, 128))
    image_path = tmp_path / "test_rgba_image.png"
    image.save(image_path)
    return image_path


@pytest.fixture
def large_image_path(tmp_path: Path) -> Path:
    """Create a temporary large image file (2001x2001) for testing size limits.

    Returns:
        Path to a 2001x2001 RGB PNG image file that exceeds maximum size.
    """
    image = PILImage.new("RGB", (2001, 2001), color=(255, 255, 255))
    image_path = tmp_path / "large_image.png"
    image.save(image_path)
    return image_path


@pytest.fixture
def small_image_path(tmp_path: Path) -> Path:
    """Create a temporary small image file (10x10) for testing edge cases.

    Returns:
        Path to a 10x10 RGB PNG image file.
    """
    image = PILImage.new("RGB", (10, 10), color=(255, 0, 0))
    image_path = tmp_path / "small_image.png"
    image.save(image_path)
    return image_path


@pytest.fixture
def max_size_image_path(tmp_path: Path) -> Path:
    """Create a temporary image file at maximum allowed size (2000x2000).

    Returns:
        Path to a 2000x2000 RGB PNG image file.
    """
    image = PILImage.new("RGB", (2000, 2000), color=(128, 128, 128))
    image_path = tmp_path / "max_size_image.png"
    image.save(image_path)
    return image_path


@pytest.fixture
def sample_image_model() -> ImageModel:
    """Create a sample ImageModel for testing.

    Returns:
        ImageModel instance with 100x100 RGB image data.
    """
    width, height = 100, 100
    pixel_data = np.zeros((height, width, 3), dtype=np.uint8)
    pixel_data[:, :] = [255, 87, 51]  # Set to a specific color

    return ImageModel(
        width=width,
        height=height,
        pixel_data=pixel_data,
        original_pixel_data=pixel_data.copy(),
        format="PNG",
        has_alpha=False,
    )


@pytest.fixture
def sample_rgba_image_model() -> ImageModel:
    """Create a sample RGBA ImageModel for testing.

    Returns:
        ImageModel instance with 100x100 RGBA image data with transparency.
    """
    width, height = 100, 100
    pixel_data = np.zeros((height, width, 4), dtype=np.uint8)
    pixel_data[:, :] = [255, 87, 51, 128]  # Set to a specific color with alpha

    return ImageModel(
        width=width,
        height=height,
        pixel_data=pixel_data,
        original_pixel_data=pixel_data.copy(),
        format="PNG",
        has_alpha=True,
    )


@pytest.fixture
def settings_model() -> SettingsModel:
    """Create a SettingsModel instance for testing.

    Returns:
        SettingsModel with default values.
    """
    return SettingsModel()


@pytest.fixture
def image_loader() -> ImageLoader:
    """Create an ImageLoader instance for testing.

    Returns:
        ImageLoader service instance.
    """
    return ImageLoader()


@pytest.fixture
def image_saver() -> ImageSaver:
    """Create an ImageSaver instance for testing.

    Returns:
        ImageSaver service instance.
    """
    return ImageSaver()


@pytest.fixture
def pixelizer() -> Pixelizer:
    """Create a Pixelizer instance for testing.

    Returns:
        Pixelizer service instance.
    """
    return Pixelizer()


@pytest.fixture
def color_reducer() -> ColorReducer:
    """Create a ColorReducer instance for testing.

    Returns:
        ColorReducer service instance.
    """
    return ColorReducer()


@pytest.fixture
def controller(
    settings_model: SettingsModel,
    image_loader: ImageLoader,
    image_saver: ImageSaver,
    pixelizer: Pixelizer,
    color_reducer: ColorReducer,
) -> MainController:
    """Create a MainController instance with all services for testing.

    Args:
        settings_model: Settings model instance.
        image_loader: Image loader service.
        image_saver: Image saver service.
        pixelizer: Pixelizer service.
        color_reducer: Color reducer service.

    Returns:
        MainController instance with all dependencies initialized.
    """
    return MainController(
        settings_model=settings_model,
        image_loader=image_loader,
        image_saver=image_saver,
        pixelizer=pixelizer,
        color_reducer=color_reducer,
    )


@pytest.fixture
def controller_minimal(settings_model: SettingsModel) -> MainController:
    """Create a minimal MainController instance for testing.

    Args:
        settings_model: Settings model instance.

    Returns:
        MainController instance with minimal dependencies (no services).
    """
    return MainController(settings_model=settings_model)

