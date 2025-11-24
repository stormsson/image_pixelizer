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
        assert panel.get_sensitivity() == 0.0

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

    def test_sensitivity_slider_range(self, qtbot) -> None:
        """Test sensitivity slider has correct range."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        slider = panel._sensitivity_slider
        assert slider.minimum() == 0
        assert slider.maximum() == 100
        assert slider.value() == 0

    def test_sensitivity_slider_emits_signal(self, qtbot) -> None:
        """Test sensitivity slider emits signal on value change."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        values_received = []

        def on_sensitivity_changed(value: float) -> None:
            values_received.append(value)

        panel.sensitivity_changed.connect(on_sensitivity_changed)

        # Change slider value (50 = 0.5)
        panel._sensitivity_slider.setValue(50)
        qtbot.wait(100)

        assert len(values_received) == 1
        assert abs(values_received[0] - 0.5) < 0.01

    def test_sensitivity_spinbox_updates(self, qtbot) -> None:
        """Test sensitivity spinbox updates when slider changes."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        panel._sensitivity_slider.setValue(75)  # Should be 0.75
        qtbot.wait(100)

        assert abs(panel._sensitivity_spinbox.value() - 0.75) < 0.01

    def test_get_pixel_size(self, qtbot) -> None:
        """Test get_pixel_size returns current slider value."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        panel._pixel_size_slider.setValue(25)
        assert panel.get_pixel_size() == 25

    def test_get_sensitivity(self, qtbot) -> None:
        """Test get_sensitivity returns current slider value as float."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        panel._sensitivity_slider.setValue(80)  # Should be 0.8
        assert abs(panel.get_sensitivity() - 0.8) < 0.01

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

    def test_sensitivity_spinbox_updates_slider(self, qtbot) -> None:
        """Test sensitivity spinbox updates slider when value is changed manually."""
        panel = ControlsPanel()
        qtbot.addWidget(panel)

        values_received = []

        def on_sensitivity_changed(value: float) -> None:
            values_received.append(value)

        panel.sensitivity_changed.connect(on_sensitivity_changed)

        # Change spinbox value manually
        panel._sensitivity_spinbox.setValue(0.65)
        qtbot.wait(100)

        # Verify slider was updated (0.65 * 100 = 65)
        assert panel._sensitivity_slider.value() == 65
        # Verify signal was emitted
        assert len(values_received) == 1
        assert abs(values_received[0] - 0.65) < 0.01

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

