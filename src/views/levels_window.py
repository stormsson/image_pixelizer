"""Image Levels tool window with histogram and sliders."""

from typing import Optional, TYPE_CHECKING

import numpy as np
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QShowEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
    QSpinBox,
    QMessageBox,
)

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel
from src.services.levels_adjuster import LevelsAdjuster


class HistogramWidget(QWidget):
    """Custom widget for displaying histogram as vertical bars.

    Displays histogram with dark tones on the left and light tones on the right.
    Bar heights are proportional to frequency counts.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize histogram widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._histogram_data: Optional[np.ndarray] = None
        self.setMinimumHeight(150)
        self.setMinimumWidth(300)

    def set_histogram_data(self, data: np.ndarray) -> None:
        """Update histogram data and trigger repaint.

        Args:
            data: Histogram data array of shape (256,) with frequency counts
        """
        self._histogram_data = data.copy() if data is not None else None
        self.update()  # Trigger paintEvent

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw histogram bars.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Draw background
        painter.fillRect(0, 0, width, height, QColor(240, 240, 240))

        if self._histogram_data is None or self._histogram_data.sum() == 0:
            # No data to display
            return

        # Normalize histogram data for better visibility
        # Use 95th percentile instead of max to prevent outliers from compressing other bars
        # This makes the histogram bars more visible and readable
        max_frequency = float(self._histogram_data.max())
        
        if max_frequency == 0:
            return

        # Use percentile-based normalization to avoid extreme outliers
        # Find the 95th percentile to use as scaling factor
        sorted_frequencies = np.sort(self._histogram_data)
        percentile_95_idx = int(len(sorted_frequencies) * 0.95)
        percentile_95 = float(sorted_frequencies[percentile_95_idx]) if percentile_95_idx < len(sorted_frequencies) else max_frequency
        
        # Use the larger of 95th percentile or 10% of max to ensure good visibility
        # This prevents very small bars when there's one dominant tone
        normalization_factor = max(percentile_95, max_frequency * 0.1)
        
        if normalization_factor == 0:
            return

        # Normalize with a scale factor to make bars more visible
        # Scale by 0.95 to leave some headroom at the top
        normalized = (self._histogram_data.astype(np.float32) / normalization_factor) * 0.95
        # Clamp to 0.0-1.0 range
        normalized = np.clip(normalized, 0.0, 1.0)

        # Calculate bar width - ensure bars fill the entire width
        # Each of the 256 bins should be evenly distributed across the full width
        # Use exact floating point calculation to avoid rounding errors
        bar_width = width / 256.0

        # Draw bars for all 256 bins to fill the entire width
        # Each bar represents one tone level (0-255) on the horizontal axis
        # Bar at index i represents tone level i, positioned from left (dark) to right (light)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(100, 100, 100))

        for i in range(256):
            bar_height = normalized[i] * height
            # Calculate x position: bar i should start at i * bar_width
            x = i * bar_width
            
            # Calculate bar width: each bar should be bar_width wide
            # For the last bar, ensure it extends exactly to the right edge
            if i == 255:
                bar_w = width - x
            else:
                bar_w = bar_width
            
            # Draw bar if it has any height
            if bar_height > 0:
                # Draw from bottom up
                painter.drawRect(
                    int(x),
                    int(height - bar_height),
                    max(1, int(np.ceil(bar_w))),  # At least 1 pixel wide, round up to avoid gaps
                    int(bar_height),
                )


class LevelsWindow(QMainWindow):
    """Window for Image Levels tool with histogram and sliders.

    Displays histogram of image tonal distribution and provides sliders
    for adjusting darks and lights cutoffs. Updates image in real-time.
    """

    # Signal emitted when levels adjustment is applied
    levels_adjusted = Signal(ImageModel)

    def __init__(
        self, controller: "MainController", parent: Optional[QWidget] = None
    ) -> None:
        """Initialize Levels tool window.

        Args:
            controller: MainController instance for image access and updates
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._controller = controller
        self._levels_adjuster = LevelsAdjuster()
        self._histogram_widget: Optional[HistogramWidget] = None
        self._darks_slider: Optional[QSlider] = None
        self._lights_slider: Optional[QSlider] = None
        self._darks_spinbox: Optional[QSpinBox] = None
        self._lights_spinbox: Optional[QSpinBox] = None
        self._current_image: Optional[ImageModel] = None
        self._base_image_for_levels: Optional[ImageModel] = None  # Base state when window opened
        self._cached_histogram: Optional[np.ndarray] = None
        self._cached_image_id: Optional[int] = None  # Track which image the histogram is for
        self._snapshot_captured: bool = False  # Track if snapshot has been captured
        self._original_image_reference: Optional[int] = None  # Reference to original image for change detection

    def showEvent(self, event: QShowEvent) -> None:
        """Handle window show event.
        
        Resets snapshot when window is shown to ensure fresh snapshot capture.
        This ensures that each time the window is opened, it captures the current image state.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        # Reset snapshot when window is shown to capture fresh state
        # This ensures that reopening the window captures the current image state
        # Only reset if window was previously hidden (snapshot was already captured)
        # If snapshot wasn't captured yet (first show), _update_histogram will capture it
        if self._snapshot_captured:
            self._snapshot_captured = False
            self._original_image_reference = None
        # Always update histogram when shown to ensure snapshot is captured
        self._update_histogram()

        self.setWindowTitle("Image Levels")
        self.setMinimumSize(400, 300)

        self._setup_ui()
        self._connect_signals()

        # Load current image and calculate histogram
        # Note: snapshot will be captured when image is available
        # If window is shown, showEvent will also trigger update
        self._update_histogram()

    def _setup_ui(self) -> None:
        """Setup user interface components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Histogram widget
        self._histogram_widget = HistogramWidget()
        layout.addWidget(self._histogram_widget)

        # Darks cutoff slider
        darks_layout = QHBoxLayout()
        darks_label = QLabel("Darks Cutoff:")
        darks_layout.addWidget(darks_label)
        self._darks_slider = QSlider(Qt.Orientation.Horizontal)
        self._darks_slider.setMinimum(0)
        self._darks_slider.setMaximum(100)
        self._darks_slider.setValue(0)
        darks_layout.addWidget(self._darks_slider)
        self._darks_spinbox = QSpinBox()
        self._darks_spinbox.setMinimum(0)
        self._darks_spinbox.setMaximum(100)
        self._darks_spinbox.setValue(0)
        self._darks_spinbox.setSuffix("%")
        self._darks_spinbox.setMinimumWidth(60)
        darks_layout.addWidget(self._darks_spinbox)
        layout.addLayout(darks_layout)

        # Lights cutoff slider
        lights_layout = QHBoxLayout()
        lights_label = QLabel("Lights Cutoff:")
        lights_layout.addWidget(lights_label)
        self._lights_slider = QSlider(Qt.Orientation.Horizontal)
        self._lights_slider.setMinimum(0)
        self._lights_slider.setMaximum(100)
        self._lights_slider.setValue(0)
        lights_layout.addWidget(self._lights_slider)
        self._lights_spinbox = QSpinBox()
        self._lights_spinbox.setMinimum(0)
        self._lights_spinbox.setMaximum(100)
        self._lights_spinbox.setValue(0)
        self._lights_spinbox.setSuffix("%")
        self._lights_spinbox.setMinimumWidth(60)
        lights_layout.addWidget(self._lights_spinbox)
        layout.addLayout(lights_layout)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Connect sliders to handlers
        if self._darks_slider:
            self._darks_slider.valueChanged.connect(self._on_darks_slider_changed)
        if self._lights_slider:
            self._lights_slider.valueChanged.connect(self._on_lights_slider_changed)
        
        # Connect spinboxes to sliders (bidirectional)
        if self._darks_spinbox and self._darks_slider:
            self._darks_spinbox.valueChanged.connect(self._darks_slider.setValue)
            self._darks_slider.valueChanged.connect(self._darks_spinbox.setValue)
        if self._lights_spinbox and self._lights_slider:
            self._lights_spinbox.valueChanged.connect(self._lights_slider.setValue)
            self._lights_slider.valueChanged.connect(self._lights_spinbox.setValue)

        # Connect to controller signals
        if self._controller:
            self._controller.image_updated.connect(self._on_image_updated)

    def _update_histogram(self, force_recapture: bool = False) -> None:
        """Calculate and display histogram for current image.
        
        Caches histogram when image loads and only recalculates when image changes.
        Does not recalculate on slider changes (uses cached histogram).
        Captures base image state when window first opens for reversible adjustments.
        
        Args:
            force_recapture: If True, force recapture of snapshot (for new image loads)
        """
        current_image = self._get_current_image()
        if current_image is None:
            self._cached_histogram = None
            self._cached_image_id = None
            self._base_image_for_levels = None
            self._snapshot_captured = False
            self._original_image_reference = None
            if self._histogram_widget:
                self._histogram_widget.set_histogram_data(None)
            self._set_sliders_enabled(False)
            return

        # Use image object reference to detect truly new images (not just pixel data changes)
        image_reference = id(current_image)
        image_id = id(current_image.pixel_data)
        
        # Check if this is a truly new image (different object reference)
        is_new_image = (
            self._original_image_reference is None
            or self._original_image_reference != image_reference
        )
        
        # Only recapture snapshot if:
        # 1. Snapshot not yet captured (first time)
        # 2. Force recapture requested (new image loaded)
        # 3. Truly new image detected (different image object)
        should_capture_snapshot = (
            not self._snapshot_captured
            or force_recapture
            or is_new_image
        )
        
        # Only recalculate histogram if image changed or not yet calculated
        if self._cached_image_id != image_id or self._cached_histogram is None or should_capture_snapshot:
            # Capture base image state only when window first opens or truly new image loaded
            # This allows levels adjustment to be reversible
            if should_capture_snapshot:
                self._base_image_for_levels = ImageModel(
                    width=current_image.width,
                    height=current_image.height,
                    pixel_data=current_image.pixel_data.copy(),
                    original_pixel_data=current_image.original_pixel_data.copy(),
                    format=current_image.format,
                    has_alpha=current_image.has_alpha,
                )
                self._snapshot_captured = True
                self._original_image_reference = image_reference
            
            self._current_image = current_image
            self._cached_image_id = image_id

            try:
                # Calculate histogram from base snapshot
                histogram = self._levels_adjuster.calculate_histogram(self._base_image_for_levels)
                self._cached_histogram = histogram

                # Display histogram
                if self._histogram_widget:
                    self._histogram_widget.set_histogram_data(histogram)

                self._set_sliders_enabled(True)
            except ValueError as e:
                # Invalid image - show user-friendly error
                self._cached_histogram = None
                self._cached_image_id = None
                self._base_image_for_levels = None
                self._snapshot_captured = False
                self._original_image_reference = None
                if self._histogram_widget:
                    self._histogram_widget.set_histogram_data(None)
                self._set_sliders_enabled(False)
                QMessageBox.warning(
                    self,
                    "Cannot Calculate Histogram",
                    f"Unable to calculate histogram for this image: {str(e)}\n\nPlease ensure the image is valid and try again.",
                )
            except Exception as e:
                # Other errors - show generic error message
                self._cached_histogram = None
                self._cached_image_id = None
                self._base_image_for_levels = None
                self._snapshot_captured = False
                self._original_image_reference = None
                if self._histogram_widget:
                    self._histogram_widget.set_histogram_data(None)
                self._set_sliders_enabled(False)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while calculating the histogram: {str(e)}\n\nThe image may be corrupted or in an unsupported format.",
                )
        else:
            # Image hasn't changed, use cached histogram
            if self._histogram_widget and self._cached_histogram is not None:
                self._histogram_widget.set_histogram_data(self._cached_histogram)
            self._set_sliders_enabled(True)

    def _get_current_image(self) -> Optional[ImageModel]:
        """Get current image from controller.

        Returns:
            Current ImageModel or None if no image loaded
        """
        if self._controller and hasattr(self._controller, "get_current_image"):
            return self._controller.get_current_image()
        elif self._controller and hasattr(self._controller, "image_model"):
            return self._controller.image_model
        return None

    def _set_sliders_enabled(self, enabled: bool) -> None:
        """Enable or disable sliders and spinboxes.

        Args:
            enabled: Whether to enable sliders and spinboxes
        """
        if self._darks_slider:
            self._darks_slider.setEnabled(enabled)
        if self._lights_slider:
            self._lights_slider.setEnabled(enabled)
        if self._darks_spinbox:
            self._darks_spinbox.setEnabled(enabled)
        if self._lights_spinbox:
            self._lights_spinbox.setEnabled(enabled)

    def _on_darks_slider_changed(self, value: int) -> None:
        """Handle darks slider value change.

        Args:
            value: New slider value (0-100)
        """
        # Spinbox will be updated automatically via signal connection
        # Apply levels adjustment
        self._apply_levels_adjustment()

    def _on_lights_slider_changed(self, value: int) -> None:
        """Handle lights slider value change.

        Args:
            value: New slider value (0-100)
        """
        # Spinbox will be updated automatically via signal connection
        # Apply levels adjustment
        self._apply_levels_adjustment()

    def _apply_levels_adjustment(self) -> None:
        """Apply levels adjustment based on current slider values.
        
        Always applies to the base image state captured when window opened,
        not the current modified state. This allows the adjustment to be reversible.
        Uses cached histogram for base image. Only recalculates histogram
        for the adjusted image to show updated distribution.
        """
        if self._base_image_for_levels is None:
            return

        if self._darks_slider is None or self._lights_slider is None:
            return

        darks_cutoff = float(self._darks_slider.value())
        lights_cutoff = float(self._lights_slider.value())

        try:
            # Always apply levels adjustment to the base image state
            # This ensures the adjustment can be reversed via undo
            adjusted_image = self._levels_adjuster.apply_levels(
                self._base_image_for_levels, darks_cutoff, lights_cutoff
            )

            # Update histogram to reflect changes in adjusted image
            # This is necessary to show the new distribution after adjustment
            try:
                updated_histogram = self._levels_adjuster.calculate_histogram(adjusted_image)
                if self._histogram_widget:
                    self._histogram_widget.set_histogram_data(updated_histogram)
            except Exception as e:
                # If histogram calculation fails for adjusted image, show error
                # but still allow the adjustment to be applied
                pass

            # Emit signal to update main view
            self.levels_adjusted.emit(adjusted_image)
        except ValueError as e:
            # Invalid input - show user-friendly error message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Invalid Input",
                f"Cannot apply levels adjustment: {str(e)}",
            )
        except Exception as e:
            # Other errors - show generic error message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while applying levels adjustment: {str(e)}",
            )

    def _on_image_updated(self, image: ImageModel) -> None:
        """Handle image update from controller.

        Args:
            image: Updated ImageModel
        """
        # Only recapture snapshot if this is a truly new image
        # Do NOT recapture if the update came from our own levels adjustment
        # This ensures the snapshot remains based on the state when window opened
        
        # If snapshot not captured yet, capture it now
        if not self._snapshot_captured:
            self._update_histogram()
            return
        
        # Check if this is a truly new image by comparing original_pixel_data
        # If original_pixel_data is different, it's a new image load
        # If original_pixel_data matches our snapshot, it's the same image (possibly modified by us)
        if self._base_image_for_levels is not None:
            # Compare original_pixel_data to detect new image loads
            # New images will have different original_pixel_data
            current_image = self._get_current_image()
            if current_image is not None:
                # Check if original_pixel_data is different (new image loaded)
                is_new_image = not np.array_equal(
                    current_image.original_pixel_data,
                    self._base_image_for_levels.original_pixel_data
                )
                
                if is_new_image:
                    # Truly new image loaded - recapture snapshot
                    self._update_histogram(force_recapture=True)
                # Otherwise, ignore the update (it's from our own adjustment or same image)

