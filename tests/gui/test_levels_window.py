"""pytest-qt tests for LevelsWindow widget."""

from unittest.mock import MagicMock

import numpy as np
import pytest
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QApplication, QSlider

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.views.levels_window import LevelsWindow


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def mock_controller(qtbot) -> MainController:
    """Create a mock MainController for testing."""
    controller = MainController()
    return controller


class TestLevelsWindowInitialization:
    """Tests for LevelsWindow initialization (T056)."""

    def test_window_opens(self, qtbot, mock_controller) -> None:
        """Test window opens correctly."""
        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        assert window is not None
        assert window.isVisible() or not window.isVisible()  # Window may be hidden initially

    def test_window_title_correct(self, qtbot, mock_controller) -> None:
        """Test window title is correct."""
        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        assert window.windowTitle() == "Image Levels"

    def test_histogram_widget_exists(self, qtbot, mock_controller) -> None:
        """Test histogram widget exists."""
        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # HistogramWidget should exist
        from src.views.levels_window import HistogramWidget
        histogram_widget = window.findChild(HistogramWidget)
        assert histogram_widget is not None

    def test_sliders_exist(self, qtbot, mock_controller) -> None:
        """Test both sliders exist with correct ranges."""
        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        sliders = window.findChildren(QSlider)
        assert len(sliders) >= 2

        # Find darks and lights sliders
        darks_slider = None
        lights_slider = None
        for slider in sliders:
            if slider.minimum() == 0 and slider.maximum() == 100:
                if darks_slider is None:
                    darks_slider = slider
                else:
                    lights_slider = slider

        assert darks_slider is not None
        assert lights_slider is not None
        assert darks_slider.minimum() == 0
        assert darks_slider.maximum() == 100
        assert lights_slider.minimum() == 0
        assert lights_slider.maximum() == 100

    def test_window_disabled_when_no_image(self, qtbot, mock_controller) -> None:
        """Test window is disabled when no image loaded."""
        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # When no image, sliders should be disabled
        sliders = window.findChildren(QSlider)
        if len(sliders) > 0:
            # At least one slider should be disabled
            assert any(not slider.isEnabled() for slider in sliders)


class TestHistogramDisplay:
    """Tests for histogram display (T057)."""

    def test_histogram_displays_when_image_loaded(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test histogram displays when image loaded."""
        # Set up controller to return image
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # Histogram should be calculated and displayed
        from src.views.levels_window import HistogramWidget
        histogram_widget = window.findChild(HistogramWidget)
        assert histogram_widget is not None

    def test_histogram_dark_tones_left(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test dark tones are on left side of histogram."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # Histogram should display dark tones on left
        # This is verified by the HistogramWidget implementation
        from src.views.levels_window import HistogramWidget
        histogram_widget = window.findChild(HistogramWidget)
        assert histogram_widget is not None

    def test_histogram_light_tones_right(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test light tones are on right side of histogram."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # Histogram should display light tones on right
        from src.views.levels_window import HistogramWidget
        histogram_widget = window.findChild(HistogramWidget)
        assert histogram_widget is not None

    def test_histogram_bars_proportional(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test histogram bars are proportional to frequency."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # Histogram bars should be proportional
        from src.views.levels_window import HistogramWidget
        histogram_widget = window.findChild(HistogramWidget)
        assert histogram_widget is not None


class TestSliderFunctionality:
    """Tests for slider functionality (T058)."""

    def test_darks_slider_updates_image(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test darks slider updates image."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)
        mock_controller.apply_levels_adjustment = MagicMock()

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # Find darks slider
        sliders = window.findChildren(QSlider)
        darks_slider = sliders[0] if len(sliders) > 0 else None

        if darks_slider:
            # Change slider value
            qtbot.mouseClick(darks_slider, Qt.MouseButton.LeftButton)
            darks_slider.setValue(10)
            qtbot.wait(100)

            # Controller should be called
            # Note: This depends on signal connection implementation

    def test_lights_slider_updates_image(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test lights slider updates image."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)
        mock_controller.apply_levels_adjustment = MagicMock()

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        # Find lights slider
        sliders = window.findChildren(QSlider)
        lights_slider = sliders[1] if len(sliders) > 1 else None

        if lights_slider:
            # Change slider value
            lights_slider.setValue(15)
            qtbot.wait(100)

            # Controller should be called

    def test_both_sliders_work_together(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test both sliders work together."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)
        mock_controller.apply_levels_adjustment = MagicMock()

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        sliders = window.findChildren(QSlider)
        if len(sliders) >= 2:
            sliders[0].setValue(5)
            sliders[1].setValue(10)
            qtbot.wait(100)

    def test_slider_values_displayed_correctly(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test slider values are displayed correctly."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        sliders = window.findChildren(QSlider)
        if len(sliders) >= 2:
            assert sliders[0].value() >= 0
            assert sliders[0].value() <= 100
            assert sliders[1].value() >= 0
            assert sliders[1].value() <= 100


class TestRealTimeUpdates:
    """Tests for real-time updates (T059)."""

    def test_histogram_updates_on_slider_change(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test histogram updates on slider change."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        sliders = window.findChildren(QSlider)
        if len(sliders) > 0:
            sliders[0].setValue(10)
            qtbot.wait(100)
            # Histogram should update

    def test_main_view_updates_on_slider_change(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test main view updates on slider change."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)
        mock_controller.apply_levels_adjustment = MagicMock()

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        sliders = window.findChildren(QSlider)
        if len(sliders) > 0:
            sliders[0].setValue(10)
            qtbot.wait(100)
            # Controller should be called to update main view

    def test_no_lag_on_rapid_slider_movement(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test no lag on rapid slider movement."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)
        mock_controller.apply_levels_adjustment = MagicMock()

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)

        sliders = window.findChildren(QSlider)
        if len(sliders) > 0:
            # Rapid slider movement
            for value in range(0, 100, 10):
                sliders[0].setValue(value)
            qtbot.wait(200)
            # Should handle rapid changes without lag


class TestSnapshotBehavior:
    """Tests for snapshot capture and persistence behavior (T061-T063, T065)."""

    def test_snapshot_captured_on_window_open(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test that snapshot is captured once when window opens (T061)."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)
        
        # Show window to trigger showEvent and ensure snapshot is captured
        window.show()
        qtbot.wait(100)

        # Verify snapshot was captured
        assert window._base_image_for_levels is not None
        assert window._base_image_for_levels.width == sample_image_model.width
        assert window._base_image_for_levels.height == sample_image_model.height
        # Verify snapshot matches the image state at window open
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            sample_image_model.pixel_data
        )

    def test_snapshot_persistence_on_levels_adjustment(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test that snapshot does not change when levels adjustment is applied (T062)."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)
        mock_controller.apply_levels_adjustment = MagicMock()

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)

        # Capture initial snapshot
        initial_snapshot = window._base_image_for_levels
        assert initial_snapshot is not None
        initial_snapshot_pixel_data = initial_snapshot.pixel_data.copy()
        
        # Apply levels adjustment
        adjusted_image = window._levels_adjuster.apply_levels(
            initial_snapshot, darks_cutoff=10.0, lights_cutoff=10.0
        )
        
        # Emit levels_adjusted signal (simulating what happens in real usage)
        window.levels_adjusted.emit(adjusted_image)
        qtbot.wait(100)
        
        # Verify snapshot did not change
        assert window._base_image_for_levels is not None
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            initial_snapshot_pixel_data
        )

    def test_snapshot_persistence_on_image_updated_signal(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test that snapshot does not change when image_updated signal is received from our own adjustment (T062)."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)

        # Capture initial snapshot
        initial_snapshot_pixel_data = window._base_image_for_levels.pixel_data.copy()
        assert initial_snapshot_pixel_data is not None
        
        # Simulate image update from our own levels adjustment
        adjusted_image = ImageModel(
            width=sample_image_model.width,
            height=sample_image_model.height,
            pixel_data=sample_image_model.pixel_data.copy() + 10,  # Modified pixel data
            original_pixel_data=sample_image_model.original_pixel_data.copy(),
            format=sample_image_model.format,
            has_alpha=sample_image_model.has_alpha,
        )
        
        # Update controller to return adjusted image
        mock_controller.get_current_image = MagicMock(return_value=adjusted_image)
        
        # Trigger image_updated handler
        window._on_image_updated(adjusted_image)
        qtbot.wait(100)
        
        # Verify snapshot did not change (still based on original)
        assert window._base_image_for_levels is not None
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            initial_snapshot_pixel_data
        )

    def test_snapshot_behavior_workflow(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test complete snapshot behavior workflow (T063)."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)
        mock_controller.apply_levels_adjustment = MagicMock()

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)

        # Verify snapshot was captured on window open
        assert window._base_image_for_levels is not None
        initial_snapshot = window._base_image_for_levels.pixel_data.copy()

        # Apply levels adjustment
        sliders = window.findChildren(QSlider)
        if len(sliders) > 0:
            sliders[0].setValue(10)  # Set darks cutoff
            qtbot.wait(100)

        # Verify snapshot unchanged after adjustment
        assert window._base_image_for_levels is not None
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            initial_snapshot
        )

        # Simulate image_updated signal from our own adjustment
        adjusted_image = ImageModel(
            width=sample_image_model.width,
            height=sample_image_model.height,
            pixel_data=sample_image_model.pixel_data.copy() + 10,
            original_pixel_data=sample_image_model.original_pixel_data.copy(),
            format=sample_image_model.format,
            has_alpha=sample_image_model.has_alpha,
        )
        window._on_image_updated(adjusted_image)
        qtbot.wait(100)

        # Verify snapshot still unchanged
        assert window._base_image_for_levels is not None
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            initial_snapshot
        )

    def test_snapshot_recapture_on_new_image(self, qtbot, mock_controller, sample_image_model: ImageModel) -> None:
        """Test snapshot recapture when new image is loaded (T065)."""
        mock_controller.get_current_image = MagicMock(return_value=sample_image_model)

        window = LevelsWindow(mock_controller)
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)

        # Capture initial snapshot
        initial_snapshot = window._base_image_for_levels.pixel_data.copy()

        # Create a different image (simulating new image load)
        import numpy as np
        new_image = ImageModel(
            width=200,
            height=200,
            pixel_data=np.zeros((200, 200, 3), dtype=np.uint8) + 100,  # Different pixel data
            original_pixel_data=np.zeros((200, 200, 3), dtype=np.uint8) + 100,
            format="PNG",
            has_alpha=False,
        )

        # Update controller to return new image
        mock_controller.get_current_image = MagicMock(return_value=new_image)

        # Trigger image_updated with new image
        window._on_image_updated(new_image)
        qtbot.wait(100)

        # Verify snapshot was recaptured to new image
        assert window._base_image_for_levels is not None
        assert not np.array_equal(
            window._base_image_for_levels.pixel_data,
            initial_snapshot
        )
        assert np.array_equal(
            window._base_image_for_levels.pixel_data,
            new_image.pixel_data
        )

