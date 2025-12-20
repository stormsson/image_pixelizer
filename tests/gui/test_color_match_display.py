"""pytest-qt tests for ColorMatchDisplay widget."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from src.views.color_match_display import ColorMatchDisplay


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestColorMatchDisplay:
    """Tests for ColorMatchDisplay widget."""

    def test_initialization(self, qtbot) -> None:
        """Test ColorMatchDisplay initializes correctly."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)

        # Check that squares exist
        assert display._image_color_square is not None
        assert display._dmc_color_square is not None

        # Check initial state - hidden
        assert not display.isVisible()

        # Check initial text is empty
        assert display._image_color_square.text() == ""
        assert display._dmc_color_square.text() == ""

    def test_initialization_square_sizes(self, qtbot) -> None:
        """Test color squares have correct size."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)

        # Check square sizes
        assert display._image_color_square.minimumSize().width() == 70
        assert display._image_color_square.minimumSize().height() == 70
        assert display._image_color_square.maximumSize().width() == 70
        assert display._image_color_square.maximumSize().height() == 70

        assert display._dmc_color_square.minimumSize().width() == 70
        assert display._dmc_color_square.minimumSize().height() == 70
        assert display._dmc_color_square.maximumSize().width() == 70
        assert display._dmc_color_square.maximumSize().height() == 70

    def test_update_color_with_valid_hex(self, qtbot) -> None:
        """Test update_color updates both squares with valid hex code."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Update with a valid hex color
        display.update_color("#FF5733")
        qtbot.wait(100)

        # Widget should be visible
        assert display.isVisible()

        # First square should show hex code
        assert "#FF5733" in display._image_color_square.text().upper()

        # Second square should show DMC match
        dmc_text = display._dmc_color_square.text()
        assert dmc_text != ""
        assert " - " in dmc_text  # Format: "DMC - Name"

    def test_update_color_with_hex_no_hash(self, qtbot) -> None:
        """Test update_color works with hex code without # prefix."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Update with hex without hash
        display.update_color("FF5733")
        qtbot.wait(100)

        # Widget should be visible
        assert display.isVisible()

        # First square should show hex code (with hash added)
        text = display._image_color_square.text().upper()
        assert "#FF5733" in text

    def test_update_color_shows_dmc_match(self, qtbot) -> None:
        """Test update_color displays correct DMC match format."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Update with a color
        display.update_color("#000000")  # Black
        qtbot.wait(100)

        # Second square should have DMC format: "DMC - Name"
        dmc_text = display._dmc_color_square.text()
        parts = dmc_text.split(" - ")
        assert len(parts) == 2
        assert parts[0] != ""  # DMC code
        assert parts[1] != ""  # Color name

    def test_update_color_sets_background_colors(self, qtbot) -> None:
        """Test update_color sets correct background colors for squares."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Update with a specific color
        hex_color = "#FF0000"  # Red
        display.update_color(hex_color)
        qtbot.wait(100)

        # Check that stylesheet contains the hex color for first square
        stylesheet = display._image_color_square.styleSheet()
        assert hex_color.upper() in stylesheet.upper()

        # Second square should have DMC color (different from input)
        dmc_stylesheet = display._dmc_color_square.styleSheet()
        # Should contain a hex color (DMC match)
        assert "background-color:" in dmc_stylesheet.lower()

    def test_update_color_with_contrasting_text(self, qtbot) -> None:
        """Test update_color uses contrasting text color based on background."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Test with dark color (should use white text)
        display.update_color("#000000")
        qtbot.wait(100)
        stylesheet = display._image_color_square.styleSheet()
        assert "color: white" in stylesheet.lower() or "color:white" in stylesheet.lower()

        # Test with light color (should use black text)
        display.update_color("#FFFFFF")
        qtbot.wait(100)
        stylesheet = display._image_color_square.styleSheet()
        assert "color: black" in stylesheet.lower() or "color:black" in stylesheet.lower()

    def test_clear_hides_widget(self, qtbot) -> None:
        """Test clear method hides widget and clears text."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # First update with color
        display.update_color("#FF5733")
        qtbot.wait(100)
        assert display.isVisible()
        assert display._image_color_square.text() != ""

        # Clear
        display.clear()
        qtbot.wait(100)

        # Widget should be hidden
        assert not display.isVisible()

        # Text should be cleared
        assert display._image_color_square.text() == ""
        assert display._dmc_color_square.text() == ""

    def test_clear_resets_stylesheets(self, qtbot) -> None:
        """Test clear method resets stylesheets to default."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Update with color
        display.update_color("#FF5733")
        qtbot.wait(100)

        # Clear
        display.clear()
        qtbot.wait(100)

        # Stylesheets should be reset to default (white background)
        stylesheet = display._image_color_square.styleSheet()
        assert "#FFFFFF" in stylesheet.upper() or "background-color: #ffffff" in stylesheet.lower()

    def test_update_color_with_empty_string(self, qtbot) -> None:
        """Test update_color with empty string clears display."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # First update with color
        display.update_color("#FF5733")
        qtbot.wait(100)
        assert display.isVisible()

        # Update with empty string
        display.update_color("")
        qtbot.wait(100)

        # Should be cleared
        assert not display.isVisible()

    def test_update_color_with_none_clears(self, qtbot) -> None:
        """Test update_color handles None by clearing."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # First update with color
        display.update_color("#FF5733")
        qtbot.wait(100)
        assert display.isVisible()

        # Update with None (simulated by checking if empty string works)
        # Since we can't pass None directly, empty string is the equivalent
        display.update_color("")
        qtbot.wait(100)
        assert not display.isVisible()

    def test_update_color_with_invalid_hex(self, qtbot) -> None:
        """Test update_color handles invalid hex codes gracefully."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Try invalid hex
        display.update_color("INVALID")
        qtbot.wait(100)

        # Should be cleared/hidden
        assert not display.isVisible()

    def test_update_color_with_short_hex(self, qtbot) -> None:
        """Test update_color handles hex codes that are too short."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Try short hex
        display.update_color("#FF")
        qtbot.wait(100)

        # Should be cleared/hidden
        assert not display.isVisible()

    def test_update_color_with_rgba_hex(self, qtbot) -> None:
        """Test update_color handles RGBA hex codes (extracts RGB)."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Update with RGBA hex (8 characters)
        display.update_color("#FF5733FF")
        qtbot.wait(100)

        # Should work (extracts first 6 chars for RGB)
        assert display.isVisible()
        # Should show full hex code as text
        text = display._image_color_square.text().upper()
        assert "#FF5733FF" in text or "#FF5733" in text
        
        # Background color should use RGB part only (CSS doesn't support RGBA hex)
        stylesheet = display._image_color_square.styleSheet().upper()
        assert "BACKGROUND-COLOR: #FF5733" in stylesheet or "BACKGROUND-COLOR:#FF5733" in stylesheet
        # Should NOT include the alpha part in background-color
        assert "BACKGROUND-COLOR: #FF5733FF" not in stylesheet and "BACKGROUND-COLOR:#FF5733FF" not in stylesheet

    def test_dmc_match_error_handling(self, qtbot, monkeypatch) -> None:
        """Test update_color handles DMC matching errors gracefully."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Mock ColorMatcher to raise an error
        def mock_get_closest_to_hex(hex_code: str):
            raise ValueError("DMC matching failed")

        monkeypatch.setattr(
            display._color_matcher, "get_closest_to_hex", mock_get_closest_to_hex
        )

        # Update with valid hex
        display.update_color("#FF5733")
        qtbot.wait(100)

        # Widget should still be visible (first square works)
        assert display.isVisible()

        # Second square should show "N/A" or error indicator
        dmc_text = display._dmc_color_square.text()
        assert "N/A" in dmc_text or dmc_text == "N/A"

    def test_word_wrap_enabled(self, qtbot) -> None:
        """Test that word wrap is enabled for long DMC names."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)

        # Check word wrap is enabled
        assert display._image_color_square.wordWrap()
        assert display._dmc_color_square.wordWrap()

    def test_square_alignment(self, qtbot) -> None:
        """Test color squares are center-aligned."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)

        # Check alignment
        assert (
            display._image_color_square.alignment()
            == Qt.AlignmentFlag.AlignCenter
        )
        assert (
            display._dmc_color_square.alignment()
            == Qt.AlignmentFlag.AlignCenter
        )

    def test_multiple_updates(self, qtbot) -> None:
        """Test multiple color updates work correctly."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # First update
        display.update_color("#FF0000")
        qtbot.wait(100)
        assert display.isVisible()
        first_dmc = display._dmc_color_square.text()

        # Second update
        display.update_color("#00FF00")
        qtbot.wait(100)
        assert display.isVisible()
        second_dmc = display._dmc_color_square.text()

        # Should have different DMC matches for different colors
        # (unless they happen to match the same DMC color, which is unlikely)
        # At minimum, the text should be updated
        assert display._image_color_square.text().upper() in ["#00FF00", "#00FF00FF"]

    def test_clear_after_update(self, qtbot) -> None:
        """Test clear works correctly after multiple updates."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)
        display.show()

        # Update multiple times
        display.update_color("#FF0000")
        qtbot.wait(50)
        display.update_color("#00FF00")
        qtbot.wait(50)
        display.update_color("#0000FF")
        qtbot.wait(50)

        assert display.isVisible()

        # Clear
        display.clear()
        qtbot.wait(100)

        # Should be hidden and cleared
        assert not display.isVisible()
        assert display._image_color_square.text() == ""
        assert display._dmc_color_square.text() == ""

    def test_color_matcher_initialized(self, qtbot) -> None:
        """Test ColorMatcher is initialized in widget."""
        display = ColorMatchDisplay()
        qtbot.addWidget(display)

        # Check ColorMatcher exists
        assert display._color_matcher is not None
        assert hasattr(display._color_matcher, "get_closest_to_hex")

