"""pytest-qt tests for StatusBar widget."""

import pytest
from PySide6.QtWidgets import QApplication

from src.models.image_model import ImageStatistics
from src.views.status_bar import StatusBar


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestStatusBar:
    """Tests for StatusBar widget."""

    def test_initialization(self, qtbot) -> None:
        """Test StatusBar initializes correctly."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        # Check that label exists and has default text
        label = status_bar.findChild(status_bar._stats_label.__class__)
        assert label is not None
        assert label.text() == "No image loaded"

    def test_update_statistics_none(self, qtbot) -> None:
        """Test update_statistics with None."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        status_bar.update_statistics(None)

        assert status_bar._stats_label.text() == "No image loaded"

    def test_update_statistics_with_dimensions(self, qtbot) -> None:
        """Test update_statistics displays dimensions and color count."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        stats = ImageStatistics(
            distinct_color_count=256,
            width=100,
            height=200,
            hover_hex_color=None,
        )

        status_bar.update_statistics(stats)

        expected_text = "100 x 200 pixels | Colors: 256"
        assert status_bar._stats_label.text() == expected_text

    def test_update_statistics_with_hex_color(self, qtbot) -> None:
        """Test update_statistics displays HEX color when hover is active."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        stats = ImageStatistics(
            distinct_color_count=256,
            width=100,
            height=200,
            hover_hex_color="#FF5733",
        )

        status_bar.update_statistics(stats)

        assert status_bar._stats_label.text() == "Color: #FF5733"

    def test_update_statistics_reverts_to_normal_on_clear(self, qtbot) -> None:
        """Test update_statistics reverts to normal stats when HEX color is cleared."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        # First update with HEX color
        stats_with_hex = ImageStatistics(
            distinct_color_count=128,
            width=150,
            height=150,
            hover_hex_color="#FF5733",
        )
        status_bar.update_statistics(stats_with_hex)
        assert status_bar._stats_label.text() == "Color: #FF5733"

        # Then update without HEX color
        stats_without_hex = ImageStatistics(
            distinct_color_count=128,
            width=150,
            height=150,
            hover_hex_color=None,
        )
        status_bar.update_statistics(stats_without_hex)
        expected_text = "150 x 150 pixels | Colors: 128"
        assert status_bar._stats_label.text() == expected_text

    def test_update_statistics_formatting(self, qtbot) -> None:
        """Test update_statistics formats dimensions correctly."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        stats = ImageStatistics(
            distinct_color_count=1,
            width=2000,
            height=2000,
            hover_hex_color=None,
        )

        status_bar.update_statistics(stats)

        expected_text = "2000 x 2000 pixels | Colors: 1"
        assert status_bar._stats_label.text() == expected_text

    def test_update_statistics_rgba_hex(self, qtbot) -> None:
        """Test update_statistics displays RGBA HEX color."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        stats = ImageStatistics(
            distinct_color_count=64,
            width=50,
            height=50,
            hover_hex_color="#FF5733FF",
        )

        status_bar.update_statistics(stats)

        assert status_bar._stats_label.text() == "Color: #FF5733FF"

    def test_update_statistics_handles_leave_event(self, qtbot) -> None:
        """Test update_statistics handles mouse leave event by reverting to normal stats."""
        status_bar = StatusBar()
        qtbot.addWidget(status_bar)

        # Show HEX color first
        stats_with_hex = ImageStatistics(
            distinct_color_count=100,
            width=200,
            height=200,
            hover_hex_color="#ABCDEF",
        )
        status_bar.update_statistics(stats_with_hex)
        assert status_bar._stats_label.text() == "Color: #ABCDEF"

        # Clear HEX color (simulating leave event)
        stats_without_hex = ImageStatistics(
            distinct_color_count=100,
            width=200,
            height=200,
            hover_hex_color=None,
        )
        status_bar.update_statistics(stats_without_hex)
        assert "200 x 200 pixels" in status_bar._stats_label.text()
        assert "Colors: 100" in status_bar._stats_label.text()
        assert "Color:" not in status_bar._stats_label.text()

