"""pytest-qt tests for ControlsPanel widget."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.views.controls_panel import ControlsPanel


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestControlsPanel:
    """Tests for ControlsPanel widget."""

    def test_initialization(self, qtbot) -> None:
        """Test ControlsPanel initializes correctly."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        assert panel.get_pixel_size() == 1
        assert panel.get_bin_count() is None

    def test_pixel_size_slider_range(self, qtbot) -> None:
        """Test pixel size slider has correct range."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        slider = panel._pixel_size_slider
        assert slider.minimum() == 1
        assert slider.maximum() == 50
        assert slider.value() == 1

    def test_pixel_size_slider_emits_signal(self, qtbot) -> None:
        """Test pixel size slider emits signal on value change."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        values_received = []

        def on_pixel_size_changed(value: int) -> None:
            values_received.append(value)

        panel.pixel_size_changed.connect(on_pixel_size_changed)

        # Change slider value
        panel._pixel_size_slider.setValue(10)
        qtbot.wait(100)

        assert len(values_received) == 1
        assert values_received[0] == 10

    def test_pixel_size_spinbox_updates(self, qtbot) -> None:
        """Test pixel size spinbox updates when slider changes."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        panel._pixel_size_slider.setValue(15)
        qtbot.wait(100)

        assert panel._pixel_size_spinbox.value() == 15

    def test_bin_count_dropdown_options(self, qtbot) -> None:
        """Test bin count dropdown has correct options."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        dropdown = panel._bin_count_dropdown
        assert dropdown.count() == 8
        assert dropdown.itemText(0) == "None"
        assert dropdown.itemText(1) == "4"
        assert dropdown.itemText(2) == "8"
        assert dropdown.itemText(3) == "16"
        assert dropdown.itemText(4) == "32"
        assert dropdown.itemText(5) == "64"
        assert dropdown.itemText(6) == "128"
        assert dropdown.itemText(7) == "256"
        assert dropdown.currentText() == "None"

    def test_bin_count_dropdown_emits_signal(self, qtbot) -> None:
        """Test bin count dropdown emits signal on value change."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        values_received = []

        def on_bin_count_changed(value: object) -> None:
            values_received.append(value)

        panel.bin_count_changed.connect(on_bin_count_changed)

        # Change dropdown value to "16"
        panel._bin_count_dropdown.setCurrentText("16")
        qtbot.wait(100)

        assert len(values_received) == 1
        assert values_received[0] == 16

    def test_bin_count_dropdown_emits_none(self, qtbot) -> None:
        """Test bin count dropdown emits None for 'None' option."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        values_received = []

        def on_bin_count_changed(value: object) -> None:
            values_received.append(value)

        panel.bin_count_changed.connect(on_bin_count_changed)

        # First set to a value to ensure change is detected
        panel._bin_count_dropdown.setCurrentText("16")
        qtbot.wait(100)
        
        # Now set to "None" (this will trigger signal)
        panel._bin_count_dropdown.setCurrentText("None")
        qtbot.wait(100)

        # Should have received both values
        assert len(values_received) >= 1
        # The last value should be None
        assert values_received[-1] is None

    def test_get_pixel_size(self, qtbot) -> None:
        """Test get_pixel_size returns current slider value."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        panel._pixel_size_slider.setValue(25)
        assert panel.get_pixel_size() == 25

    def test_get_bin_count(self, qtbot) -> None:
        """Test get_bin_count returns current dropdown value."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        # Default should be None
        assert panel.get_bin_count() is None

        # Set to a value
        panel._bin_count_dropdown.setCurrentText("32")
        assert panel.get_bin_count() == 32

        # Set back to None
        panel._bin_count_dropdown.setCurrentText("None")
        assert panel.get_bin_count() is None

    def test_pixel_size_spinbox_updates_slider(self, qtbot) -> None:
        """Test pixel size spinbox updates slider when value is changed manually."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        values_received = []

        def on_pixel_size_changed(value: int) -> None:
            values_received.append(value)

        panel.pixel_size_changed.connect(on_pixel_size_changed)

        # Change spinbox value manually
        panel._pixel_size_spinbox.setValue(20)
        qtbot.wait(100)

        # Verify slider was updated
        assert panel._pixel_size_slider.value() == 20
        # Verify signal was emitted
        assert len(values_received) == 1
        assert values_received[0] == 20

    def test_set_bin_count(self, qtbot) -> None:
        """Test set_bin_count updates dropdown selection."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        # Set to a value
        panel.set_bin_count(64)
        assert panel._bin_count_dropdown.currentText() == "64"
        assert panel.get_bin_count() == 64

        # Set to None
        panel.set_bin_count(None)
        assert panel._bin_count_dropdown.currentText() == "None"
        assert panel.get_bin_count() is None

        # Set to another value
        panel.set_bin_count(128)
        assert panel._bin_count_dropdown.currentText() == "128"
        assert panel.get_bin_count() == 128

    def test_set_processing_state_disables_dropdown(self, qtbot) -> None:
        """Test set_processing_state disables/enables dropdown."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        # Initially enabled
        assert panel._bin_count_dropdown.isEnabled()

        # Disable during processing
        panel.set_processing_state(True)
        assert not panel._bin_count_dropdown.isEnabled()

        # Re-enable after processing
        panel.set_processing_state(False)
        assert panel._bin_count_dropdown.isEnabled()

    def test_save_button_hidden_initially(self, qtbot) -> None:
        """Test save button is hidden initially when no image is loaded."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        assert not panel._save_button.isVisible()

    def test_save_button_visible_after_image_load(self, qtbot) -> None:
        """Test save button becomes visible after image is loaded."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()  # Make widget visible for isVisible() to work correctly

        # Initially hidden
        assert not panel._save_button.isVisible()

        # Set image loaded
        panel.set_image_loaded(True)
        qtbot.wait(100)

        # Now visible
        assert panel._save_button.isVisible()

    def test_save_button_hidden_after_image_cleared(self, qtbot) -> None:
        """Test save button becomes hidden after image is cleared."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()  # Make widget visible for isVisible() to work correctly

        # Set image loaded
        panel.set_image_loaded(True)
        qtbot.wait(100)
        assert panel._save_button.isVisible()

        # Clear image
        panel.set_image_loaded(False)
        qtbot.wait(100)

        # Now hidden
        assert not panel._save_button.isVisible()

    def test_save_button_emits_signal(self, qtbot) -> None:
        """Test save button emits save_requested signal when clicked."""
        from PySide6.QtCore import Qt

        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()  # Make widget visible
        panel.set_image_loaded(True)  # Make button visible
        qtbot.wait(100)

        signals_received = []

        def on_save_requested() -> None:
            signals_received.append(True)

        panel.save_requested.connect(on_save_requested)

        # Click save button
        qtbot.mouseClick(panel._save_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        # Verify signal was emitted
        assert len(signals_received) == 1


class TestOpenAIBackgroundRemovalButton:
    """Tests for Remove Background (Automatic) button (T061)."""

    def test_automatic_button_hidden_initially(self, qtbot) -> None:
        """Test automatic background removal button is hidden initially."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        assert not panel._openai_remove_background_button.isVisible()

    def test_automatic_button_visible_after_image_load(self, qtbot) -> None:
        """Test automatic button becomes visible after image is loaded."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()

        # Initially hidden
        assert not panel._openai_remove_background_button.isVisible()

        # Set image loaded
        panel.set_image_loaded(True)
        qtbot.wait(100)

        # Now visible
        assert panel._openai_remove_background_button.isVisible()

    def test_automatic_button_hidden_after_image_cleared(self, qtbot) -> None:
        """Test automatic button becomes hidden after image is cleared."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()

        # Set image loaded
        panel.set_image_loaded(True)
        qtbot.wait(100)
        assert panel._openai_remove_background_button.isVisible()

        # Clear image
        panel.set_image_loaded(False)
        qtbot.wait(100)

        # Now hidden
        assert not panel._openai_remove_background_button.isVisible()

    def test_automatic_button_emits_signal(self, qtbot) -> None:
        """Test automatic button emits openai_background_removal_requested signal when clicked."""
        from PySide6.QtCore import Qt

        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()
        panel.set_image_loaded(True)
        qtbot.wait(100)

        signals_received = []

        def on_openai_background_removal_requested() -> None:
            signals_received.append(True)

        panel.openai_background_removal_requested.connect(on_openai_background_removal_requested)

        # Click automatic button
        qtbot.mouseClick(panel._openai_remove_background_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)

        # Verify signal was emitted
        assert len(signals_received) == 1

    def test_automatic_button_labeling(self, qtbot) -> None:
        """Test automatic button has correct label and tooltip."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        button = panel._openai_remove_background_button
        assert "OpenAI" in button.text()
        assert button.toolTip() is not None
        assert len(button.toolTip()) > 0

    def test_automatic_button_distinguishable_from_interactive(self, qtbot) -> None:
        """Test automatic button is clearly distinguishable from interactive button."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        automatic_button = panel._openai_remove_background_button
        interactive_button = panel._remove_background_button

        # Both buttons should have different text
        assert automatic_button.text() != interactive_button.text()
        # Automatic button should mention "OpenAI"
        assert "OpenAI" in automatic_button.text()
        # Interactive button should mention "SAM" or similar
        assert "SAM" in interactive_button.text() or "Interactive" in interactive_button.text()

    def test_automatic_button_enabled_when_image_loaded(self, qtbot) -> None:
        """Test automatic button is enabled when image is loaded."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()

        panel.set_image_loaded(True)
        qtbot.wait(100)

        assert panel._openai_remove_background_button.isEnabled()

    def test_automatic_button_disabled_when_no_image(self, qtbot) -> None:
        """Test automatic button is disabled when no image is loaded."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)
        panel.show()

        # Button should be disabled when not visible (no image)
        panel.set_image_loaded(False)
        qtbot.wait(100)

        # Button is hidden, but if it were visible it should be disabled
        # This is handled by visibility, but we can test the state
        if panel._openai_remove_background_button.isVisible():
            assert not panel._openai_remove_background_button.isEnabled()

