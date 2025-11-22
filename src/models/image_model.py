"""Image data model and statistics."""

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class ImageModel:
    """Represents a loaded image with pixel data and metadata.

    This model holds both the current processed pixel data and the original
    unprocessed pixel data, allowing effects to be applied and reset.

    Attributes:
        width: Image width in pixels.
        height: Image height in pixels.
        pixel_data: NumPy array of shape (height, width, channels) containing
            current processed pixel data. Channels can be 3 (RGB) or 4 (RGBA).
        original_pixel_data: NumPy array containing the original unprocessed
            pixel data. Used as the base for applying effects.
        format: Image format string (e.g., "PNG", "JPEG").
        has_alpha: Whether the image has an alpha channel (transparency).

    Raises:
        ValueError: If dimensions are invalid, pixel_data is not a NumPy array,
            or array shape is invalid.
    """

    width: int
    height: int
    pixel_data: np.ndarray
    original_pixel_data: np.ndarray
    format: str
    has_alpha: bool

    def __post_init__(self) -> None:
        """Validate image model after initialization.

        Performs validation checks on dimensions, pixel data structure,
        and ensures image size does not exceed maximum allowed (2000x2000px).
        """
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image dimensions must be greater than 0")
        if self.width > 2000 or self.height > 2000:
            raise ValueError(
                "Image size exceeds maximum of 2000x2000 pixels. "
                "Please resize the image."
            )
        if not isinstance(self.pixel_data, np.ndarray):
            raise ValueError("pixel_data must be a NumPy array")
        if len(self.pixel_data.shape) != 3:
            raise ValueError("pixel_data must have shape (height, width, channels)")
        if self.pixel_data.shape[2] not in (3, 4):
            raise ValueError("pixel_data must have 3 (RGB) or 4 (RGBA) channels")


@dataclass
class ImageStatistics:
    """Computed statistics about the current image state.

    This model holds computed information about the image that is displayed
    in the status bar. It includes dimensions, color count, and optional
    hover color information.

    Attributes:
        distinct_color_count: Number of unique colors in the processed image.
            Must be >= 1.
        width: Image width in pixels.
        height: Image height in pixels.
        hover_hex_color: Optional HEX color code (e.g., "#FF5733") of the pixel
            currently under the mouse cursor. None when mouse is not over image.

    Raises:
        ValueError: If distinct_color_count < 1 or hover_hex_color is not
            in valid HEX format.
    """

    distinct_color_count: int
    width: int
    height: int
    hover_hex_color: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate statistics after initialization.

        Validates that distinct_color_count is positive and hover_hex_color
        (if provided) is in valid HEX format.
        """
        if self.distinct_color_count < 1:
            raise ValueError("distinct_color_count must be >= 1")
        if self.hover_hex_color is not None:
            if not self._is_valid_hex(self.hover_hex_color):
                raise ValueError(
                    f"hover_hex_color must be valid HEX format, got: {self.hover_hex_color}"
                )

    @staticmethod
    def _is_valid_hex(hex_str: str) -> bool:
        """Check if string is valid HEX color format.

        Args:
            hex_str: String to validate.

        Returns:
            True if string is valid HEX format (#RRGGBB or #RRGGBBAA),
            False otherwise.
        """
        if not hex_str.startswith("#"):
            return False
        hex_part = hex_str[1:]
        if len(hex_part) not in (6, 8):  # RGB or RGBA
            return False
        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False


def rgb_to_hex(r: int, g: int, b: int, a: Optional[int] = None) -> str:
    """
    Convert RGB/RGBA values to HEX color string.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        a: Optional alpha component (0-255)

    Returns:
        HEX color string (e.g., "#FF5733" or "#FF5733FF")
    """
    if a is not None:
        return f"#{r:02X}{g:02X}{b:02X}{a:02X}"
    return f"#{r:02X}{g:02X}{b:02X}"

