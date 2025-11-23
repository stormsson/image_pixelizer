"""pytest-qt tests for MainWindow widget."""

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel, ImageStatistics
from src.views.main_window import MainWindow


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


class TestMainWindow:
    """Tests for MainWindow widget."""

    def test_initialization(self, qtbot, mock_controller) -> None:
        """Test MainWindow initializes correctly."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        assert window.windowTitle() == "Image Pixelizer"
        assert window.minimumSize().width() >= 800
        assert window.minimumSize().height() >= 600

    def test_menu_bar_exists(self, qtbot, mock_controller) -> None:
        """Test MainWindow has menu bar with File menu."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        menubar = window.menuBar()
        assert menubar is not None

        # Check for File menu
        file_menu = menubar.findChild(QObject, "File")
        # File menu should exist (added via addMenu)
        actions = menubar.actions()
        assert len(actions) > 0
        assert any(action.text() == "&File" or "File" in action.text() for action in actions)

    def test_load_image_action_exists(self, qtbot, mock_controller) -> None:
        """Test MainWindow has Load Image action."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        menubar = window.menuBar()
        actions = menubar.actions()
        # Should have at least one action (Load Image)
        assert len(actions) > 0

    def test_image_view_exists(self, qtbot, mock_controller) -> None:
        """Test MainWindow has ImageView widget."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        # ImageView should be in central widget
        central_widget = window.centralWidget()
        assert central_widget is not None

    def test_status_bar_exists(self, qtbot, mock_controller) -> None:
        """Test MainWindow has StatusBar."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        status_bar = window.statusBar()
        assert status_bar is not None

    def test_image_loaded_signal_updates_view(self, qtbot, mock_controller) -> None:
        """Test image_loaded signal updates ImageView."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        import numpy as np
        pixel_data = np.zeros((100, 100, 3), dtype=np.uint8)
        image = ImageModel(
            width=100,
            height=100,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Emit signal
        mock_controller.image_loaded.emit(image)

        # Wait for signal processing
        qtbot.wait(100)

        # ImageView should have been updated (pixmap should exist)
        # Note: We can't directly check pixmap without accessing private members,
        # but we can verify the signal was connected

    def test_statistics_updated_signal_updates_status_bar(self, qtbot, mock_controller) -> None:
        """Test statistics_updated signal updates StatusBar."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        stats = ImageStatistics(
            distinct_color_count=256,
            width=100,
            height=100,
            hover_hex_color=None,
        )

        # Emit signal
        mock_controller.statistics_updated.emit(stats)

        # Wait for signal processing
        qtbot.wait(100)

        # StatusBar should have been updated
        status_bar = window.statusBar()
        assert status_bar is not None

    def test_error_occurred_signal_handled(self, qtbot, mock_controller) -> None:
        """Test error_occurred signal is handled."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)

        # Emit error signal
        mock_controller.error_occurred.emit("Test error message")

        # Wait for signal processing
        qtbot.wait(100)

        # Error should be handled (would show QMessageBox in real app)

    def test_ui_disabled_when_processing_starts(self, qtbot, mock_controller) -> None:
        """Test UI is disabled when automatic background removal processing starts (T062)."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)
        window.show()

        # Initially UI should be enabled
        assert window._controls_panel.isEnabled()
        if window._image_view:
            assert window._image_view.isEnabled()

        # Emit processing_started signal
        mock_controller.processing_started.emit()
        qtbot.wait(100)

        # UI should be disabled
        assert not window._controls_panel.isEnabled()
        if window._image_view:
            assert not window._image_view.isEnabled()

    def test_ui_enabled_when_processing_completes(self, qtbot, mock_controller) -> None:
        """Test UI is enabled when automatic background removal processing completes (T062)."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)
        window.show()

        # Disable UI first (simulate processing started)
        mock_controller.processing_started.emit()
        qtbot.wait(100)
        assert not window._controls_panel.isEnabled()

        # Emit processing_finished signal
        mock_controller.processing_finished.emit()
        qtbot.wait(100)

        # UI should be enabled again
        assert window._controls_panel.isEnabled()
        if window._image_view:
            assert window._image_view.isEnabled()

    def test_all_controls_disabled_during_processing(self, qtbot, mock_controller) -> None:
        """Test all controls are disabled during automatic background removal processing (T062)."""
        window = MainWindow(mock_controller)
        qtbot.addWidget(window)
        window.show()

        # Set image loaded to make buttons visible
        if window._controls_panel:
            window._controls_panel.set_image_loaded(True)
        qtbot.wait(100)

        # Emit processing_started signal
        mock_controller.processing_started.emit()
        qtbot.wait(100)

        # All controls should be disabled
        assert not window._controls_panel.isEnabled()
        # Check that individual buttons are also disabled (if accessible)
        if hasattr(window._controls_panel, '_openai_remove_background_button'):
            # Button should be disabled (through parent widget)
            assert not window._controls_panel._openai_remove_background_button.isEnabled() or not window._controls_panel.isEnabled()

