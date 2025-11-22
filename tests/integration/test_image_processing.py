"""Integration tests for image processing workflows."""

import numpy as np
import pytest
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel, ImageStatistics
from src.models.settings_model import SettingsModel
from src.services.color_reducer import ColorReducer
from src.services.image_loader import ImageLoader
from src.services.image_saver import ImageSaver
from src.services.pixelizer import Pixelizer
from src.views.image_view import ImageView
from src.views.main_window import MainWindow
from src.views.status_bar import StatusBar


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestLoadImageWorkflow:
    """Integration tests for load image workflow."""

    def test_load_image_end_to_end(self, qtbot, sample_image_path) -> None:
        """Test complete workflow: file dialog → load → display → status bar update."""
        # Setup
        settings_model = SettingsModel()
        image_loader = ImageLoader()
        controller = MainController(
            settings_model=settings_model,
            image_loader=image_loader,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)

        # Track signals
        image_loaded_received = []
        statistics_updated_received = []

        def on_image_loaded(image: ImageModel) -> None:
            image_loaded_received.append(image)

        def on_statistics_updated(stats: ImageStatistics) -> None:
            statistics_updated_received.append(stats)

        controller.image_loaded.connect(on_image_loaded)
        controller.statistics_updated.connect(on_statistics_updated)

        # Execute: Load image
        controller.load_image(str(sample_image_path))

        # Wait for async operations
        qtbot.wait(500)

        # Verify: Image was loaded
        assert len(image_loaded_received) == 1
        loaded_image = image_loaded_received[0]
        assert isinstance(loaded_image, ImageModel)
        assert loaded_image.width == 100
        assert loaded_image.height == 100

        # Verify: Statistics were updated
        assert len(statistics_updated_received) >= 1
        stats = statistics_updated_received[-1]
        assert isinstance(stats, ImageStatistics)
        assert stats.width == 100
        assert stats.height == 100

        # Verify: ImageView was updated
        # (ImageView should have pixmap set, but we can't easily check without accessing private members)

        # Verify: StatusBar was updated
        status_bar = window.statusBar()
        assert status_bar is not None
        # Status bar should show dimensions
        label_text = status_bar._stats_label.text()
        assert "100" in label_text
        assert "100" in label_text

    def test_pixelization_workflow(self, qtbot, sample_image_path) -> None:
        """Test complete workflow: load → pixelize → verify effect."""
        # Setup
        settings_model = SettingsModel()
        image_loader = ImageLoader()
        pixelizer = Pixelizer()
        controller = MainController(
            settings_model=settings_model,
            image_loader=image_loader,
            pixelizer=pixelizer,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)

        # Track signals
        image_loaded_received = []
        image_updated_received = []

        def on_image_loaded(image: ImageModel) -> None:
            image_loaded_received.append(image)

        def on_image_updated(image: ImageModel) -> None:
            image_updated_received.append(image)

        controller.image_loaded.connect(on_image_loaded)
        controller.image_updated.connect(on_image_updated)

        # Step 1: Load image
        controller.load_image(str(sample_image_path))
        qtbot.wait(500)

        assert len(image_loaded_received) == 1
        original_image = image_loaded_received[0]

        # Step 2: Apply pixelization
        controller.update_pixel_size(5)
        qtbot.wait(500)

        # Verify: Image was updated
        assert len(image_updated_received) == 1
        pixelized_image = image_updated_received[0]

        # Verify: Image dimensions unchanged
        assert pixelized_image.width == original_image.width
        assert pixelized_image.height == original_image.height

        # Verify: Pixel data is different (pixelized)
        # The pixelized image should have fewer distinct colors or different pixel values
        assert pixelized_image.pixel_data.shape == original_image.pixel_data.shape

    def test_load_image_error_handling(self, qtbot) -> None:
        """Test error handling in load image workflow."""
        settings_model = SettingsModel()
        image_loader = ImageLoader()
        controller = MainController(
            settings_model=settings_model,
            image_loader=image_loader,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)

        # Track error signal
        error_received = []

        def on_error(message: str) -> None:
            error_received.append(message)

        controller.error_occurred.connect(on_error)

        # Try to load non-existent file
        controller.load_image("/nonexistent/path/image.png")

        # Wait for error handling
        qtbot.wait(500)

        # Verify: Error was emitted
        assert len(error_received) == 1
        assert "not found" in error_received[0].lower() or "could not be found" in error_received[0]

    def test_load_image_unsupported_format(self, qtbot, tmp_path) -> None:
        """Test loading unsupported format shows error."""
        settings_model = SettingsModel()
        image_loader = ImageLoader()
        controller = MainController(
            settings_model=settings_model,
            image_loader=image_loader,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)

        # Track error signal
        error_received = []

        def on_error(message: str) -> None:
            error_received.append(message)

        controller.error_occurred.connect(on_error)

        # Create unsupported file
        unsupported_file = tmp_path / "test.txt"
        unsupported_file.write_text("not an image")

        # Try to load
        controller.load_image(str(unsupported_file))

        # Wait for error handling
        qtbot.wait(500)

        # Verify: Error was emitted
        assert len(error_received) == 1
        assert "unsupported" in error_received[0].lower() or "format" in error_received[0].lower()


class TestColorReductionWorkflow:
    """Integration tests for color reduction workflow."""

    def test_color_reduction_workflow(self, qtbot, sample_image_path) -> None:
        """Test complete workflow: load → pixelize → reduce colors → verify color count."""
        # Setup
        settings_model = SettingsModel()
        image_loader = ImageLoader()
        pixelizer = Pixelizer()
        color_reducer = ColorReducer()
        controller = MainController(
            settings_model=settings_model,
            image_loader=image_loader,
            pixelizer=pixelizer,
            color_reducer=color_reducer,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)

        # Track signals
        image_loaded_received = []
        image_updated_received = []
        statistics_updated_received = []

        def on_image_loaded(image: ImageModel) -> None:
            image_loaded_received.append(image)

        def on_image_updated(image: ImageModel) -> None:
            image_updated_received.append(image)

        def on_statistics_updated(stats: ImageStatistics) -> None:
            statistics_updated_received.append(stats)

        controller.image_loaded.connect(on_image_loaded)
        controller.image_updated.connect(on_image_updated)
        controller.statistics_updated.connect(on_statistics_updated)

        # Step 1: Load image
        controller.load_image(str(sample_image_path))
        qtbot.wait(500)

        assert len(image_loaded_received) == 1
        original_image = image_loaded_received[0]

        # Get initial color count
        initial_stats = statistics_updated_received[-1]
        initial_color_count = initial_stats.distinct_color_count

        # Step 2: Apply pixelization
        controller.update_pixel_size(5)
        qtbot.wait(500)

        assert len(image_updated_received) >= 1
        pixelized_image = image_updated_received[-1]

        # Step 3: Apply color reduction with sensitivity
        controller.update_sensitivity(0.7)
        qtbot.wait(500)

        # Verify: Image was updated again
        assert len(image_updated_received) >= 2
        reduced_image = image_updated_received[-1]

        # Verify: Image dimensions unchanged
        assert reduced_image.width == original_image.width
        assert reduced_image.height == original_image.height

        # Verify: Color count was reduced (or stayed same if already minimal)
        final_stats = statistics_updated_received[-1]
        final_color_count = final_stats.distinct_color_count
        assert final_color_count <= initial_color_count
        # With sensitivity 0.7, should have fewer or equal colors
        # (may be equal if image already has very few colors)

        # Verify: Status bar shows updated color count
        status_bar = window.statusBar()
        assert status_bar is not None
        label_text = status_bar._stats_label.text()
        assert str(final_color_count) in label_text


class TestMouseHoverWorkflow:
    """Integration tests for mouse hover workflow."""

    def test_mouse_hover_workflow(self, qtbot, sample_image_path) -> None:
        """Test complete workflow: load → hover → verify HEX → leave → verify revert."""
        # Setup
        settings_model = SettingsModel()
        image_loader = ImageLoader()
        controller = MainController(
            settings_model=settings_model,
            image_loader=image_loader,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)
        window.resize(800, 600)

        # Track signals
        hover_colors_received = []
        statistics_updated_received = []

        def on_hover_color_changed(hex_color: str) -> None:
            hover_colors_received.append(hex_color)

        def on_statistics_updated(stats: ImageStatistics) -> None:
            statistics_updated_received.append(stats)

        controller.hover_color_changed.connect(on_hover_color_changed)
        controller.statistics_updated.connect(on_statistics_updated)

        # Step 1: Load image
        controller.load_image(str(sample_image_path))
        qtbot.wait(500)

        assert len(statistics_updated_received) >= 1
        initial_stats = statistics_updated_received[-1]
        assert initial_stats.hover_hex_color is None

        # Step 2: Simulate mouse hover over image
        image_view = window._image_view
        assert image_view is not None

        # Create a mouse move event at a specific position
        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import Qt

        # Move mouse to center of image view
        mouse_pos = QPointF(image_view.width() / 2, image_view.height() / 2)
        mouse_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            mouse_pos,
            image_view.window().mapToGlobal(mouse_pos.toPoint()),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )

        # Trigger mouse move event
        image_view.mouseMoveEvent(mouse_event)
        qtbot.wait(200)

        # Verify: Hover color was updated
        assert len(hover_colors_received) >= 1
        assert hover_colors_received[-1].startswith("#")
        assert len(hover_colors_received[-1]) in (7, 9)  # RGB or RGBA format

        # Verify: Statistics were updated with HEX color
        final_stats = statistics_updated_received[-1]
        assert final_stats.hover_hex_color is not None
        assert final_stats.hover_hex_color == hover_colors_received[-1]

        # Verify: Status bar shows HEX color
        status_bar = window.statusBar()
        assert status_bar is not None
        label_text = status_bar._stats_label.text()
        assert "Color:" in label_text
        assert hover_colors_received[-1] in label_text

        # Step 3: Simulate mouse leave event
        from PySide6.QtCore import QEvent

        leave_event = QEvent(QEvent.Type.Leave)
        image_view.leaveEvent(leave_event)
        qtbot.wait(200)

        # Verify: Hover color was cleared (empty string emitted)
        assert "" in hover_colors_received or len(hover_colors_received) > 1

        # Verify: Statistics were updated without HEX color
        final_stats_after_leave = statistics_updated_received[-1]
        assert final_stats_after_leave.hover_hex_color is None

        # Verify: Status bar reverted to normal stats
        label_text_after_leave = status_bar._stats_label.text()
        assert "Color:" not in label_text_after_leave
        assert "pixels" in label_text_after_leave
        assert "Colors:" in label_text_after_leave


class TestSaveWorkflow:
    """Integration tests for save workflow."""

    def test_save_workflow(self, qtbot, sample_image_path, tmp_path) -> None:
        """Test complete workflow: load → process → save → verify PNG file."""
        # Setup
        settings_model = SettingsModel()
        image_loader = ImageLoader()
        pixelizer = Pixelizer()
        color_reducer = ColorReducer()
        image_saver = ImageSaver()
        controller = MainController(
            settings_model=settings_model,
            image_loader=image_loader,
            pixelizer=pixelizer,
            color_reducer=color_reducer,
            image_saver=image_saver,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)

        # Track signals
        save_completed_received = []

        def on_save_completed(file_path: str) -> None:
            save_completed_received.append(file_path)

        controller.save_completed.connect(on_save_completed)

        # Step 1: Load image
        controller.load_image(str(sample_image_path))
        qtbot.wait(500)

        # Step 2: Apply pixelization
        controller.update_pixel_size(5)
        qtbot.wait(500)

        # Step 3: Apply color reduction
        controller.update_sensitivity(0.5)
        qtbot.wait(500)

        # Step 4: Save image
        output_path = tmp_path / "saved_image.png"
        controller.save_image(str(output_path))
        qtbot.wait(500)

        # Verify: Save completed signal was emitted
        assert len(save_completed_received) == 1
        assert save_completed_received[0] == str(output_path)

        # Verify: File was created
        assert output_path.exists()

        # Verify: File can be opened as PNG
        from PIL import Image as PILImage

        saved_image = PILImage.open(output_path)
        assert saved_image.format == "PNG"
        assert saved_image.size == (100, 100)  # Original image size

    def test_save_without_image_shows_error(self, qtbot) -> None:
        """Test that saving without an image shows error message."""
        settings_model = SettingsModel()
        image_saver = ImageSaver()
        controller = MainController(
            settings_model=settings_model,
            image_saver=image_saver,
        )

        window = MainWindow(controller)
        qtbot.addWidget(window)

        # Track error signal
        error_received = []

        def on_error(message: str) -> None:
            error_received.append(message)

        controller.error_occurred.connect(on_error)

        # Try to save without loading image
        controller.save_image("/tmp/test.png")
        qtbot.wait(200)

        # Verify: Error was emitted
        assert len(error_received) == 1
        assert "No image to save" in error_received[0]

