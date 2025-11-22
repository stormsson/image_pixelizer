"""Image view widget for displaying images in main content area."""

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QPixmap, QImage, QMouseEvent
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

if TYPE_CHECKING:
    from PySide6.QtGui import QResizeEvent
    from PySide6.QtCore import QEvent

from PIL import Image as PILImage
import numpy as np

from src.models.image_model import rgb_to_hex


class ImageView(QLabel):
    """Widget for displaying images with scaling and aspect ratio preservation."""

    # Signal emitted when mouse hovers over a pixel
    pixel_color_changed = Signal(str)  # HEX color code
    pixel_color_cleared = Signal()  # Emitted when mouse leaves

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize image view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setText("No image loaded")
        self.setMouseTracking(True)  # Enable mouse tracking for hover
        self._current_pixel_data: Optional[np.ndarray] = None
        self._original_size: Optional[tuple[int, int]] = None

    def display_image(self, pixel_data: np.ndarray, width: int, height: int) -> None:
        """
        Display image scaled to fit while maintaining aspect ratio.

        Args:
            pixel_data: NumPy array of shape (height, width, channels)
            width: Original image width
            height: Original image height
        """
        # Ensure pixel data is contiguous to avoid stride/alignment issues
        pixel_data = np.ascontiguousarray(pixel_data, dtype=np.uint8)

        self._current_pixel_data = pixel_data
        self._original_size = (width, height)

        # Verify array shape matches expected dimensions
        if pixel_data.shape[0] != height or pixel_data.shape[1] != width:
            raise ValueError(
                f"Pixel data shape {pixel_data.shape} doesn't match dimensions {width}x{height}"
            )

        # Get number of channels
        channels = pixel_data.shape[2]

        # Convert NumPy array to PIL Image first (ensures proper format)
        pil_image = PILImage.fromarray(pixel_data)

        # Try using PIL's ImageQt for reliable conversion (if available)
        # Otherwise fall back to manual conversion
        try:
            from PIL import ImageQt

            qimage = ImageQt.ImageQt(pil_image)
        except (ImportError, AttributeError):
            # Fallback: Convert PIL Image to QImage using tobytes with proper format
            # This ensures correct channel order and alignment
            if channels == 4:  # RGBA
                bytes_data = pil_image.tobytes("raw", "RGBA")
                bytes_per_line = width * 4
                qimage = QImage(
                    bytes_data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGBA8888,
                )
            elif channels == 3:  # RGB
                bytes_data = pil_image.tobytes("raw", "RGB")
                bytes_per_line = width * 3
                qimage = QImage(
                    bytes_data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                )
            else:
                raise ValueError(f"Unsupported number of channels: {channels}")

        # Verify QImage is valid
        if qimage.isNull():
            raise ValueError("Failed to create QImage from pixel data")

        # Convert to QPixmap
        pixmap = QPixmap.fromImage(qimage)

        # Scale to fit widget while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled_pixmap)

    def resizeEvent(self, event: "QResizeEvent") -> None:
        """Handle widget resize to update image scaling.

        Args:
            event: Resize event from Qt.
        """
        super().resizeEvent(event)
        if self._current_pixel_data is not None and self._original_size is not None:
            width, height = self._original_size
            self.display_image(self._current_pixel_data, width, height)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move event to extract pixel color at cursor position.

        Args:
            event: Mouse move event
        """
        super().mouseMoveEvent(event)

        if self._current_pixel_data is None or self._original_size is None:
            return

        if self.pixmap() is None:
            return

        # Get mouse position relative to widget
        pos = event.position().toPoint()

        # Get pixmap and its position (centered in widget)
        pixmap = self.pixmap()
        pixmap_rect = pixmap.rect()
        widget_rect = self.rect()

        # Calculate pixmap position (centered)
        pixmap_x = (widget_rect.width() - pixmap_rect.width()) // 2
        pixmap_y = (widget_rect.height() - pixmap_rect.height()) // 2

        # Check if mouse is over the pixmap
        if (
            pixmap_x <= pos.x() < pixmap_x + pixmap_rect.width()
            and pixmap_y <= pos.y() < pixmap_y + pixmap_rect.height()
        ):
            # Convert widget coordinates to pixmap coordinates
            pixmap_pos_x = pos.x() - pixmap_x
            pixmap_pos_y = pos.y() - pixmap_y

            # Convert pixmap coordinates to original image coordinates
            scale_x = self._original_size[0] / pixmap_rect.width()
            scale_y = self._original_size[1] / pixmap_rect.height()

            image_x = int(pixmap_pos_x * scale_x)
            image_y = int(pixmap_pos_y * scale_y)

            # Clamp to valid range
            image_x = max(0, min(image_x, self._original_size[0] - 1))
            image_y = max(0, min(image_y, self._original_size[1] - 1))

            # Extract pixel color
            pixel = self._current_pixel_data[image_y, image_x]

            # Convert to HEX
            if len(pixel) == 4:  # RGBA
                hex_color = rgb_to_hex(pixel[0], pixel[1], pixel[2], pixel[3])
            else:  # RGB
                hex_color = rgb_to_hex(pixel[0], pixel[1], pixel[2])

            # Emit signal
            self.pixel_color_changed.emit(hex_color)

    def leaveEvent(self, event: "QEvent") -> None:
        """Handle mouse leave event to clear hover color.

        Args:
            event: Leave event from Qt.
        """
        super().leaveEvent(event)
        self.pixel_color_cleared.emit()

