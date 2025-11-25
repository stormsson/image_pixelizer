"""Controls panel widget with sliders for image processing."""

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QComboBox,
)


class ControlsPanel(QWidget):
    """Sidebar widget containing editing controls for image manipulation."""

    # Signals
    pixel_size_changed = Signal(int)  # pixel_size value (1-50)
    bin_count_changed = Signal(object)  # bin_count value (None, 4, 8, 16, 32, 64, 128, 256) - object for Optional[int] compatibility
    save_requested = Signal()  # Emitted when save button is clicked
    remove_background_requested = Signal()  # Emitted when remove background button is clicked
    openai_background_removal_requested = Signal()  # Emitted when automatic remove background button is clicked
    apply_requested = Signal()  # Emitted when apply button is clicked
    cancel_requested = Signal()  # Emitted when cancel button is clicked
    undo_requested = Signal()  # Emitted when undo button is clicked

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize controls panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Add margins
        layout.setSpacing(8)  # Add spacing between widgets

        # Pixel size slider
        pixel_size_label = QLabel("Pixel Size:")
        pixel_size_label.setWordWrap(True)  # Allow text wrapping
        layout.addWidget(pixel_size_label)

        # Horizontal layout for slider and spinbox
        pixel_size_row = QHBoxLayout()
        self._pixel_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._pixel_size_slider.setMinimum(1)
        self._pixel_size_slider.setMaximum(50)
        self._pixel_size_slider.setValue(1)
        self._pixel_size_slider.valueChanged.connect(self._on_pixel_size_slider_changed)
        pixel_size_row.addWidget(self._pixel_size_slider)

        self._pixel_size_spinbox = QSpinBox()
        self._pixel_size_spinbox.setMinimum(1)
        self._pixel_size_spinbox.setMaximum(50)
        self._pixel_size_spinbox.setValue(1)
        self._pixel_size_spinbox.setObjectName("pixel_size_value")
        self._pixel_size_spinbox.valueChanged.connect(self._on_pixel_size_spinbox_changed)
        self._pixel_size_spinbox.setMaximumWidth(60)  # Keep it compact
        pixel_size_row.addWidget(self._pixel_size_spinbox)

        layout.addLayout(pixel_size_row)

        # Bin count dropdown (for color reduction)
        bin_count_label = QLabel("Color Bins:")
        bin_count_label.setWordWrap(True)  # Allow text wrapping
        layout.addWidget(bin_count_label)

        self._bin_count_dropdown = QComboBox()
        self._bin_count_dropdown.addItems(["None", "4", "8", "16", "32", "64", "128", "256"])
        self._bin_count_dropdown.setCurrentText("None")  # Default
        self._bin_count_dropdown.currentTextChanged.connect(self._on_bin_count_changed)
        layout.addWidget(self._bin_count_dropdown)

        # Add spacing before buttons section
        layout.addSpacing(12)

        # Remove Background button (interactive)
        self._remove_background_button = QPushButton("Remove Background(SAM)")
        self._remove_background_button.setObjectName("remove_background_button")
        self._remove_background_button.setToolTip("Interactive background removal with point selection")
        self._remove_background_button.clicked.connect(self._on_remove_background_clicked)
        self._remove_background_button.setVisible(False)  # Hidden initially
        layout.addWidget(self._remove_background_button)
        layout.addSpacing(8)  # Spacing after Remove Background button

        # Remove Background (Automatic) button
        self._openai_remove_background_button = QPushButton("Remove Background (OpenAI)")
        self._openai_remove_background_button.setObjectName("openai_remove_background_button")
        self._openai_remove_background_button.setToolTip("Automatic background removal using AI (no point selection required)")
        self._openai_remove_background_button.clicked.connect(self._on_openai_remove_background_clicked)
        self._openai_remove_background_button.setVisible(False)  # Hidden initially
        layout.addWidget(self._openai_remove_background_button)
        layout.addSpacing(8)  # Spacing after Automatic Remove Background button

        # Apply button (for point selection)
        self._apply_button = QPushButton("Apply")
        self._apply_button.setObjectName("apply_button")
        self._apply_button.clicked.connect(self._on_apply_clicked)
        self._apply_button.setVisible(False)  # Hidden initially
        self._apply_button.setEnabled(False)  # Disabled until points are selected
        layout.addWidget(self._apply_button)
        layout.addSpacing(8)  # Spacing after Apply button

        # Cancel button (for point selection)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.setObjectName("cancel_button")
        self._cancel_button.clicked.connect(self._on_cancel_clicked)
        self._cancel_button.setVisible(False)  # Hidden initially
        layout.addWidget(self._cancel_button)
        layout.addSpacing(8)  # Spacing after Cancel button

        # Undo button
        self._undo_button = QPushButton("Undo")
        self._undo_button.setObjectName("undo_button")
        self._undo_button.clicked.connect(self._on_undo_clicked)
        self._undo_button.setVisible(False)  # Hidden initially
        self._undo_button.setEnabled(False)  # Disabled when no operations available
        layout.addWidget(self._undo_button)
        layout.addSpacing(8)  # Spacing after Undo button

        # Add spacing before Save button
        layout.addSpacing(8)

        # Save button
        self._save_button = QPushButton("Save")
        self._save_button.setObjectName("save_button")
        self._save_button.clicked.connect(self._on_save_clicked)
        self._save_button.setVisible(False)  # Hidden initially
        layout.addWidget(self._save_button)

        layout.addStretch()

        # Track if we're updating to prevent circular updates
        self._updating_pixel_size = False

    def _on_remove_background_clicked(self) -> None:
        """Handle remove background button click.

        Emits remove_background_requested signal to trigger point selection mode in controller.
        """
        self.remove_background_requested.emit()

    def _on_openai_remove_background_clicked(self) -> None:
        """Handle automatic remove background button click.

        Emits openai_background_removal_requested signal to trigger automatic background removal.
        """
        self.openai_background_removal_requested.emit()

    def _on_apply_clicked(self) -> None:
        """Handle apply button click.

        Emits apply_requested signal to trigger background removal with selected points.
        """
        self.apply_requested.emit()

    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click.

        Emits cancel_requested signal to exit point selection mode.
        """
        self.cancel_requested.emit()

    def _on_undo_clicked(self) -> None:
        """Handle undo button click.

        Emits undo_requested signal to trigger undo operation in controller.
        """
        self.undo_requested.emit()

    def _on_save_clicked(self) -> None:
        """Handle save button click.

        Emits save_requested signal to trigger save operation in controller.
        """
        self.save_requested.emit()

    def set_image_loaded(self, is_loaded: bool) -> None:
        """
        Update button visibility based on image loaded state.

        Args:
            is_loaded: True if image is loaded, False otherwise
        """
        self._remove_background_button.setVisible(is_loaded)
        self._openai_remove_background_button.setVisible(is_loaded)
        self._save_button.setVisible(is_loaded)
        self._undo_button.setVisible(is_loaded)
        # Apply and Cancel buttons are controlled by point selection mode, not image loaded state

    def set_point_selection_mode(self, is_active: bool) -> None:
        """
        Update button states based on point selection mode.

        Args:
            is_active: True when entering point selection mode, False when exiting
        """
        if is_active:
            # Entering point selection mode: hide Remove Background, show Apply/Cancel
            self._remove_background_button.setVisible(False)
            self._apply_button.setVisible(True)
            self._cancel_button.setVisible(True)
            self._apply_button.setEnabled(False)  # Disabled until points are selected
        else:
            # Exiting point selection mode: show Remove Background buttons, hide Apply/Cancel
            self._remove_background_button.setVisible(self._save_button.isVisible())  # Show if image is loaded
            self._openai_remove_background_button.setVisible(self._save_button.isVisible())  # Show if image is loaded
            self._apply_button.setVisible(False)
            self._cancel_button.setVisible(False)
            self._apply_button.setEnabled(False)

    def update_apply_button_state(self, point_count: int) -> None:
        """
        Update Apply button enabled state based on point count.

        Args:
            point_count: Number of points currently selected
        """
        self._apply_button.setEnabled(point_count > 0)

    def update_undo_state(self, can_undo: bool) -> None:
        """
        Update Undo button enabled state based on operation history.

        Args:
            can_undo: True if undo is available, False otherwise
        """
        self._undo_button.setEnabled(can_undo)

    def _on_pixel_size_slider_changed(self, value: int) -> None:
        """Handle pixel size slider value change.

        Args:
            value: New pixel size value from slider (1-50).
        """
        if not self._updating_pixel_size:
            self._updating_pixel_size = True
            self._pixel_size_spinbox.setValue(value)
            self._updating_pixel_size = False
            self.pixel_size_changed.emit(value)

    def _on_pixel_size_spinbox_changed(self, value: int) -> None:
        """Handle pixel size spinbox value change.

        Args:
            value: New pixel size value from spinbox (1-50).
        """
        if not self._updating_pixel_size:
            self._updating_pixel_size = True
            self._pixel_size_slider.setValue(value)
            self._updating_pixel_size = False
            self.pixel_size_changed.emit(value)

    def _on_bin_count_changed(self, value: str) -> None:
        """Handle bin count dropdown value change.

        Args:
            value: Selected string ("None", "4", "8", "16", "32", "64", "128", "256")

        Emits:
            bin_count_changed: With Optional[int] (None for "None", int for others)
        """
        if value == "None":
            bin_count = None
        else:
            bin_count = int(value)
        self.bin_count_changed.emit(bin_count)

    def get_pixel_size(self) -> int:
        """
        Get current pixel size value.

        Returns:
            Current pixel size (1-50)
        """
        return self._pixel_size_slider.value()

    def get_bin_count(self) -> Optional[int]:
        """
        Get current bin count selection.

        Returns:
            Current bin count (None, 4, 8, 16, 32, 64, 128, 256)
        """
        text = self._bin_count_dropdown.currentText()
        return None if text == "None" else int(text)

    def set_bin_count(self, bin_count: Optional[int]) -> None:
        """
        Set dropdown to specified bin count.

        Args:
            bin_count: Bin count to select (None, 4, 8, 16, 32, 64, 128, 256)
        """
        if bin_count is None:
            self._bin_count_dropdown.setCurrentText("None")
        else:
            self._bin_count_dropdown.setCurrentText(str(bin_count))

    def set_processing_state(self, is_processing: bool) -> None:
        """
        Enable/disable dropdown based on processing state.

        Args:
            is_processing: True to disable dropdown, False to enable
        """
        self._bin_count_dropdown.setEnabled(not is_processing)

