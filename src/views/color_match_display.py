"""Color match display widget showing image color and DMC color match."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from src.services.color_matcher import ColorMatcher


class ColorMatchDisplay(QWidget):
    """Widget displaying image color and closest DMC color match side by side."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize color match display widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._color_matcher = ColorMatcher()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup user interface components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # First square: Image color
        self._image_color_square = QLabel()
        self._image_color_square.setMinimumSize(70, 70)
        self._image_color_square.setMaximumSize(70, 70)
        self._image_color_square.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_color_square.setWordWrap(True)
        self._image_color_square.setStyleSheet(
            "border: 1px solid #888; background-color: #FFFFFF; font-size: 10px;"
        )
        self._image_color_square.setText("")
        layout.addWidget(self._image_color_square)

        # Second square: DMC color
        self._dmc_color_square = QLabel()
        self._dmc_color_square.setMinimumSize(70, 70)
        self._dmc_color_square.setMaximumSize(70, 70)
        self._dmc_color_square.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dmc_color_square.setWordWrap(True)
        self._dmc_color_square.setStyleSheet(
            "border: 1px solid #888; background-color: #FFFFFF; font-size: 9px;"
        )
        self._dmc_color_square.setText("")
        layout.addWidget(self._dmc_color_square)

        # Initially hide the widget
        self.setVisible(False)

    def _get_contrasting_text_color(self, bg_color: QColor) -> str:
        """
        Determine contrasting text color (black or white) based on background brightness.

        Args:
            bg_color: Background color

        Returns:
            "black" or "white" as string for CSS
        """
        # Calculate relative luminance (perceived brightness)
        r = bg_color.red() / 255.0
        g = bg_color.green() / 255.0
        b = bg_color.blue() / 255.0

        # Apply gamma correction
        r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4

        # Calculate relative luminance
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

        # Use white text on dark backgrounds, black on light
        return "white" if luminance < 0.5 else "black"

    def update_color(self, hex_code: str) -> None:
        """
        Update both color squares with image color and DMC match.

        Args:
            hex_code: HEX color code (e.g., "#FF5733")
        """
        if not hex_code:
            self.clear()
            return

        try:
            # Parse hex color for first square
            hex_clean = hex_code.strip().upper()
            if not hex_clean.startswith("#"):
                hex_clean = "#" + hex_clean

            # Extract RGB from hex (handle both #RRGGBB and #RRGGBBAA)
            hex_part = hex_clean[1:]
            if len(hex_part) >= 6:
                r = int(hex_part[0:2], 16)
                g = int(hex_part[2:4], 16)
                b = int(hex_part[4:6], 16)
                image_color = QColor(r, g, b)
                # Extract RGB hex for CSS (ignore alpha channel)
                rgb_hex = f"#{hex_part[0:6]}"
            else:
                # Invalid hex, clear display
                self.clear()
                return

            # Set first square color and text
            text_color = self._get_contrasting_text_color(image_color)
            self._image_color_square.setStyleSheet(
                f"border: 1px solid #888; background-color: {rgb_hex}; color: {text_color}; font-size: 10px;"
            )
            # Display the original hex code (with or without alpha) as text
            self._image_color_square.setText(hex_clean)

            # Get DMC match for second square
            try:
                dmc_match = self._color_matcher.get_closest_to_hex(hex_clean)
                dmc_rgb = dmc_match["rgb"]
                dmc_color = QColor(dmc_rgb[0], dmc_rgb[1], dmc_rgb[2])
                dmc_hex = dmc_match["hex"]
                dmc_text = f'{dmc_match["dmc"]} - {dmc_match["name"]}'

                # Set second square color and text
                dmc_text_color = self._get_contrasting_text_color(dmc_color)
                self._dmc_color_square.setStyleSheet(
                    f"border: 1px solid #888; background-color: {dmc_hex}; color: {dmc_text_color}; font-size: 9px;"
                )
                self._dmc_color_square.setText(dmc_text)
            except Exception as e:
                # If DMC matching fails, show error in second square
                self._dmc_color_square.setStyleSheet(
                    "border: 1px solid #888; background-color: #FFFFFF; color: black; font-size: 9px;"
                )
                self._dmc_color_square.setText("N/A")

            # Show the widget
            self.setVisible(True)

        except (ValueError, Exception) as e:
            # Invalid hex code or other error, clear display
            self.clear()

    def clear(self) -> None:
        """Clear display and hide widget when mouse leaves image."""
        self._image_color_square.setText("")
        self._image_color_square.setStyleSheet(
            "border: 1px solid #888; background-color: #FFFFFF;"
        )
        self._dmc_color_square.setText("")
        self._dmc_color_square.setStyleSheet(
            "border: 1px solid #888; background-color: #FFFFFF;"
        )
        self.setVisible(False)

