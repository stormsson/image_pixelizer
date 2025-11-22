"""Status bar widget for displaying image statistics."""

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QStatusBar, QLabel, QWidget

from src.models.image_model import ImageStatistics


class StatusBar(QStatusBar):
    """Status bar widget displaying image statistics and HEX color on hover."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize status bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._stats_label = QLabel("No image loaded")
        self.addWidget(self._stats_label)

    def update_statistics(self, statistics: Optional[ImageStatistics]) -> None:
        """
        Update status bar with image statistics.

        Args:
            statistics: ImageStatistics instance or None
        """
        if statistics is None:
            self._stats_label.setText("No image loaded")
            return

        # Show HEX color if hover is active, otherwise show normal stats
        if statistics.hover_hex_color:
            self._stats_label.setText(f"Color: {statistics.hover_hex_color}")
        else:
            self._stats_label.setText(
                f"{statistics.width} x {statistics.height} pixels | "
                f"Colors: {statistics.distinct_color_count}"
            )

