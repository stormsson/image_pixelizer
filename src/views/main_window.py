"""Main application window."""

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QPalette
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
)

from src.controllers.main_controller import MainController
from src.models.image_model import ImageModel, ImageStatistics
from src.views.controls_panel import ControlsPanel
from src.views.image_view import ImageView
from src.views.status_bar import StatusBar


class MainWindow(QMainWindow):
    """Main application window with menu, image view, and status bar."""

    def __init__(
        self, controller: MainController, parent: Optional[QWidget] = None
    ) -> None:
        """
        Initialize main window.

        Args:
            controller: MainController instance
            parent: Parent widget
        """
        super().__init__(parent)
        self._controller = controller
        self._image_view: Optional[ImageView] = None
        self._controls_panel: Optional[ControlsPanel] = None
        self._status_bar: Optional[StatusBar] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup user interface components."""
        self.setWindowTitle("Image Pixelizer")
        self.setMinimumSize(800, 600)

        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        # Load image action
        load_action = QAction("&Load Image...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._on_load_image)
        file_menu.addAction(load_action)

        # Save image action
        save_action = QAction("&Save Image...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_image)
        file_menu.addAction(save_action)

        # Create central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins so background fills
        layout.setSpacing(0)  # Remove spacing

        # Create container for controls panel with lighter background
        controls_container = QWidget()
        controls_container.setMinimumWidth(150)  # Ensure minimum usable width
        controls_container.setMaximumWidth(400)  # Limit controls panel width
        
        # Set background color 10% brighter than default
        palette = controls_container.palette()
        base_color = palette.color(QPalette.ColorRole.Window)
        # Lighten by 10%: blend with white (10% white, 90% original)
        lighter_color = QColor(
            int(base_color.red() + (255 - base_color.red()) * 0.1),
            int(base_color.green() + (255 - base_color.green()) * 0.1),
            int(base_color.blue() + (255 - base_color.blue()) * 0.1),
        )
        controls_container.setStyleSheet(f"background-color: {lighter_color.name()};")
        controls_container.setAutoFillBackground(True)
        
        # Create controls panel inside container
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        self._controls_panel = ControlsPanel()
        controls_layout.addWidget(self._controls_panel)
        
        layout.addWidget(controls_container)

        # Create image view
        self._image_view = ImageView()
        layout.addWidget(self._image_view, stretch=1)  # Image view takes remaining space

        # Create status bar
        self._status_bar = StatusBar()
        self.setStatusBar(self._status_bar)

    def _connect_signals(self) -> None:
        """Connect controller signals to view updates."""
        self._controller.image_loaded.connect(self._on_image_loaded)
        self._controller.image_updated.connect(self._on_image_updated)
        self._controller.statistics_updated.connect(self._on_statistics_updated)
        self._controller.error_occurred.connect(self._on_error)
        self._controller.save_completed.connect(self._on_save_completed)

        # Connect controls panel signals to controller
        if self._controls_panel:
            self._controls_panel.pixel_size_changed.connect(
                self._controller.update_pixel_size
            )
            self._controls_panel.sensitivity_changed.connect(
                self._controller.update_sensitivity
            )

        # Connect image view mouse hover signals to controller
        if self._image_view:
            self._image_view.pixel_color_changed.connect(
                self._controller.update_hover_color
            )
            self._image_view.pixel_color_cleared.connect(
                self._controller.clear_hover_color
            )

        # Connect controls panel save button to controller
        if self._controls_panel:
            self._controls_panel.save_requested.connect(self._on_save_image)

    def _on_load_image(self) -> None:
        """Handle load image menu action."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.gif *.bmp *.webp);;All Files (*)",
        )

        if file_path:
            self._controller.load_image(file_path)

    def _on_save_image(self) -> None:
        """Handle save image menu action."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG Files (*.png);;All Files (*)",
        )

        if file_path:
            self._controller.save_image(file_path)

    def _on_save_completed(self, file_path: str) -> None:
        """
        Handle save completed signal.

        Args:
            file_path: Path where image was saved
        """
        QMessageBox.information(
            self, "Save Successful", f"Image saved successfully to:\n{file_path}"
        )

    def _on_image_loaded(self, image: ImageModel) -> None:
        """
        Handle image loaded signal.

        Args:
            image: Loaded ImageModel instance
        """
        if self._image_view:
            self._image_view.display_image(
                image.pixel_data, image.width, image.height
            )
        
        # Update controls panel to show save button
        if self._controls_panel:
            self._controls_panel.set_image_loaded(True)

    def _on_image_updated(self, image: ImageModel) -> None:
        """
        Handle image updated signal (e.g., after pixelization).

        Args:
            image: Updated ImageModel instance
        """
        if self._image_view:
            self._image_view.display_image(
                image.pixel_data, image.width, image.height
            )
        
        # Ensure save button remains visible after image updates
        if self._controls_panel:
            self._controls_panel.set_image_loaded(True)

    def _on_statistics_updated(self, statistics: ImageStatistics) -> None:
        """
        Handle statistics updated signal.

        Args:
            statistics: Updated ImageStatistics instance
        """
        if self._status_bar:
            self._status_bar.update_statistics(statistics)

    def _on_error(self, error_message: str) -> None:
        """
        Handle error signal.

        Args:
            error_message: Error message to display
        """
        QMessageBox.critical(self, "Error", error_message)

