"""Main controller coordinating models, services, and views."""

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import QObject, Signal, QThread

from src.models.image_model import ImageModel, ImageStatistics
from src.models.point_selection import PointSelectionCollection
from src.models.settings_model import SettingsModel

if TYPE_CHECKING:
    from src.services.background_remover import BackgroundRemover
    from src.services.color_reducer import ColorReducer
    from src.services.image_loader import ImageLoader
    from src.services.image_saver import ImageSaver
    from src.services.operation_history import OperationHistoryManager
    from src.services.pixelizer import Pixelizer


class MainController(QObject):
    """Coordinates application components following MVC pattern."""

    # Signals
    image_loaded = Signal(ImageModel)
    image_updated = Signal(ImageModel)
    statistics_updated = Signal(ImageStatistics)
    hover_color_changed = Signal(str)  # HEX color code or None
    error_occurred = Signal(str)  # error message
    save_completed = Signal(str)  # file path
    point_selection_mode_active = Signal(bool)  # True when entering, False when exiting
    point_added = Signal(int, int, str)  # x, y, label (keep/remove)
    processing_started = Signal()  # Emitted when background removal processing begins
    processing_finished = Signal()  # Emitted when background removal processing completes (success or error)
    operation_history_changed = Signal()  # Emitted when operation history changes (for undo button state updates)

    def __init__(
        self,
        image_model: Optional[ImageModel] = None,
        settings_model: Optional[SettingsModel] = None,
        image_loader: Optional["ImageLoader"] = None,
        image_saver: Optional["ImageSaver"] = None,
        pixelizer: Optional["Pixelizer"] = None,
        color_reducer=None,  # ColorReducer - will be set later
        background_remover: Optional["BackgroundRemover"] = None,
    ) -> None:
        """
        Initialize controller with dependencies.

        Args:
            image_model: Image data model
            settings_model: Application settings model
            image_loader: Image loading service
            image_saver: Image saving service
            pixelizer: Pixelization service
            color_reducer: Color reduction service
            background_remover: Background removal service
        """
        super().__init__()
        self._image_model = image_model
        self._settings_model = settings_model or SettingsModel()
        self._image_loader = image_loader
        self._image_saver = image_saver
        self._pixelizer = pixelizer
        self._color_reducer = color_reducer
        self._background_remover = background_remover
        self._statistics: Optional[ImageStatistics] = None
        self._background_removal_thread: Optional[QThread] = None
        self._background_removal_worker: Optional["BackgroundRemovalWorker"] = None
        self._point_selection_collection = PointSelectionCollection()
        # Initialize operation history manager
        from src.services.operation_history import OperationHistoryManager
        self._operation_history = OperationHistoryManager()


    @property
    def image_model(self) -> Optional[ImageModel]:
        """Get current image model.

        Returns:
            Current ImageModel instance or None if no image loaded.
        """
        return self._image_model

    def can_undo(self) -> bool:
        """Check if undo is available.

        Returns:
            True if there are operations in history to undo, False otherwise
        """
        return self._operation_history.can_undo()

    def load_image(self, file_path: str) -> None:
        """
        Load image from file path.

        Args:
            file_path: Path to image file

        Emits:
            image_loaded: When image successfully loaded
            error_occurred: If loading fails
        """
        if self._image_loader is None:
            self.error_occurred.emit("Image loader not initialized")
            return

        try:
            image = self._image_loader.load_image(file_path)
            self._image_model = image
            # Clear operation history when new image is loaded
            self._operation_history.clear()
            self.operation_history_changed.emit()
            self._update_statistics()
            self.image_loaded.emit(image)
            if self._statistics:
                self.statistics_updated.emit(self._statistics)
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "user_message"):
                error_msg = e.user_message
            self.error_occurred.emit(error_msg)

    def get_statistics(self) -> Optional[ImageStatistics]:
        """
        Get current image statistics.

        Returns:
            Current ImageStatistics instance or None if no image loaded
        """
        return self._statistics

    def _update_statistics(self) -> None:
        """Update statistics from current image model.

        Computes distinct color count and updates ImageStatistics instance.
        Preserves hover_hex_color if it was previously set.
        """
        if self._image_model is None:
            self._statistics = None
            return

        # Compute distinct color count using ColorReducer's method if available
        # Otherwise fall back to manual calculation
        if self._color_reducer is not None:
            from src.services.color_reducer import ColorReducer

            unique_colors = ColorReducer.count_distinct_colors(
                self._image_model.pixel_data
            )
        else:
            # Fallback: manual calculation
            pixel_data = self._image_model.pixel_data
            pixels = pixel_data.reshape(-1, pixel_data.shape[2])
            unique_colors = len(set(tuple(p) for p in pixels))

        self._statistics = ImageStatistics(
            distinct_color_count=unique_colors,
            width=self._image_model.width,
            height=self._image_model.height,
            hover_hex_color=self._statistics.hover_hex_color
            if self._statistics
            else None,
        )

    def update_pixel_size(self, pixel_size: int) -> None:
        """
        Update pixel size and apply pixelization.

        Args:
            pixel_size: New pixel size value (1-50)

        Emits:
            image_updated: When pixelization is applied
            statistics_updated: When statistics are updated
            error_occurred: If pixelization fails
        """
        if self._image_model is None:
            return

        if self._pixelizer is None:
            self.error_occurred.emit("Pixelizer not initialized")
            return

        try:
            # Update settings
            self._settings_model.pixelization.pixel_size = pixel_size
            self._settings_model.pixelization.is_enabled = pixel_size > 1

            # Always start from original image for pixelization
            original_image = ImageModel(
                width=self._image_model.width,
                height=self._image_model.height,
                pixel_data=self._image_model.original_pixel_data.copy(),
                original_pixel_data=self._image_model.original_pixel_data.copy(),
                format=self._image_model.format,
                has_alpha=self._image_model.has_alpha,
            )

            # Apply pixelization on original image
            pixelized_image = self._pixelizer.pixelize(original_image, pixel_size)

            # Apply color reduction if enabled (after pixelization)
            if (
                self._color_reducer is not None
                and self._settings_model.color_reduction.is_enabled
            ):
                sensitivity = self._settings_model.color_reduction.sensitivity
                pixelized_image = self._color_reducer.reduce_colors(
                    pixelized_image, sensitivity
                )

            # Update model (preserve original_pixel_data)
            self._image_model = ImageModel(
                width=pixelized_image.width,
                height=pixelized_image.height,
                pixel_data=pixelized_image.pixel_data,
                original_pixel_data=self._image_model.original_pixel_data.copy(),
                format=pixelized_image.format,
                has_alpha=pixelized_image.has_alpha,
            )

            # Update statistics
            self._update_statistics()

            # Emit signals
            self.image_updated.emit(pixelized_image)
            if self._statistics:
                self.statistics_updated.emit(self._statistics)
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "user_message"):
                error_msg = e.user_message
            self.error_occurred.emit(error_msg)

    def update_sensitivity(self, sensitivity: float) -> None:
        """
        Update sensitivity and apply color reduction.

        Color reduction is applied after pixelization if pixelization is enabled.

        Args:
            sensitivity: New sensitivity value (0.0-1.0)

        Emits:
            image_updated: When color reduction is applied
            statistics_updated: When statistics are updated
            error_occurred: If color reduction fails
        """
        if self._image_model is None:
            return

        if self._color_reducer is None:
            self.error_occurred.emit("Color reducer not initialized")
            return

        try:
            # Update settings
            self._settings_model.color_reduction.sensitivity = sensitivity
            self._settings_model.color_reduction.is_enabled = sensitivity > 0.0

            # Always start from original image
            original_image = ImageModel(
                width=self._image_model.width,
                height=self._image_model.height,
                pixel_data=self._image_model.original_pixel_data.copy(),
                original_pixel_data=self._image_model.original_pixel_data.copy(),
                format=self._image_model.format,
                has_alpha=self._image_model.has_alpha,
            )

            # If pixelization is enabled, apply it first on original
            if (
                self._pixelizer is not None
                and self._settings_model.pixelization.is_enabled
            ):
                pixel_size = self._settings_model.pixelization.pixel_size
                original_image = self._pixelizer.pixelize(original_image, pixel_size)

            # Apply color reduction
            reduced_image = self._color_reducer.reduce_colors(
                original_image, sensitivity
            )

            # Update model (preserve original_pixel_data)
            self._image_model = ImageModel(
                width=reduced_image.width,
                height=reduced_image.height,
                pixel_data=reduced_image.pixel_data,
                original_pixel_data=self._image_model.original_pixel_data.copy(),
                format=reduced_image.format,
                has_alpha=reduced_image.has_alpha,
            )

            # Update statistics using ColorReducer's count method
            self._update_statistics()

            # Emit signals
            self.image_updated.emit(reduced_image)
            if self._statistics:
                self.statistics_updated.emit(self._statistics)
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "user_message"):
                error_msg = e.user_message
            self.error_occurred.emit(error_msg)

    def update_hover_color(self, hex_color: str) -> None:
        """
        Update hover color in statistics.

        Args:
            hex_color: HEX color code string (e.g., "#FF5733")
        """
        if self._statistics is None:
            return

        # Update statistics with new hover color
        self._statistics = ImageStatistics(
            distinct_color_count=self._statistics.distinct_color_count,
            width=self._statistics.width,
            height=self._statistics.height,
            hover_hex_color=hex_color,
        )

        # Emit signals
        self.hover_color_changed.emit(hex_color)
        self.statistics_updated.emit(self._statistics)

    def clear_hover_color(self) -> None:
        """Clear hover color and revert to normal statistics display."""
        if self._statistics is None:
            return

        # Update statistics without hover color
        self._statistics = ImageStatistics(
            distinct_color_count=self._statistics.distinct_color_count,
            width=self._statistics.width,
            height=self._statistics.height,
            hover_hex_color=None,
        )

        # Emit signals
        self.hover_color_changed.emit("")
        self.statistics_updated.emit(self._statistics)

    def save_image(self, file_path: str) -> None:
        """
        Save current processed image to file.

        Args:
            file_path: Path where image should be saved

        Emits:
            save_completed: When image is successfully saved
            error_occurred: If saving fails
        """
        if self._image_model is None:
            self.error_occurred.emit("No image to save. Please load an image first.")
            return

        if self._image_saver is None:
            self.error_occurred.emit("Image saver not initialized")
            return

        try:
            self._image_saver.save_image(self._image_model, file_path)
            self.save_completed.emit(file_path)
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "user_message"):
                error_msg = e.user_message
            self.error_occurred.emit(error_msg)

    def enter_point_selection_mode(self) -> None:
        """
        Enter point selection mode for interactive background removal.

        Emits:
            point_selection_mode_active: True when entering mode
        """
        if self._image_model is None:
            self.error_occurred.emit("No image loaded. Please load an image first.")
            return

        self._point_selection_collection.is_active = True
        self.point_selection_mode_active.emit(True)

    def exit_point_selection_mode(self) -> None:
        """
        Exit point selection mode and clear all points.

        Emits:
            point_selection_mode_active: False when exiting mode
        """
        self._point_selection_collection.is_active = False
        self._point_selection_collection.clear()
        self.point_selection_mode_active.emit(False)

    def add_point(self, x: int, y: int, label: str) -> None:
        """
        Add a point to the point selection collection.

        Args:
            x: X coordinate in image pixel space
            y: Y coordinate in image pixel space
            label: "keep" (foreground) or "remove" (background)

        Emits:
            point_added: When point is successfully added (x, y, label)
            error_occurred: If point is invalid or out of bounds
        """
        if not self._point_selection_collection.is_active:
            return

        if self._image_model is None:
            self.error_occurred.emit("No image loaded.")
            return

        # Validate coordinates are within image bounds
        if x < 0 or x >= self._image_model.width:
            self.error_occurred.emit(f"X coordinate {x} is out of bounds (0-{self._image_model.width - 1})")
            return

        if y < 0 or y >= self._image_model.height:
            self.error_occurred.emit(f"Y coordinate {y} is out of bounds (0-{self._image_model.height - 1})")
            return

        try:
            self._point_selection_collection.add_point(x, y, label)
            self.point_added.emit(x, y, label)
        except ValueError as e:
            self.error_occurred.emit(str(e))

    def clear_points(self) -> None:
        """Clear all points from the point selection collection."""
        self._point_selection_collection.clear()

    def cancel_point_selection(self) -> None:
        """
        Cancel point selection mode and clear all points.

        Emits:
            point_selection_mode_active: False when canceling
        """
        self.exit_point_selection_mode()

    def apply_background_removal(self) -> None:
        """
        Apply background removal using selected points.

        Converts points to SAM prompts, calls BackgroundRemover with prompts,
        updates ImageModel, and exits point selection mode.

        Emits:
            image_updated: When background removal is complete
            point_selection_mode_active: False when exiting mode
            error_occurred: If background removal fails
        """
        if self._image_model is None:
            self.error_occurred.emit("No image to process. Please load an image first.")
            return

        if not self._point_selection_collection.is_active:
            self.error_occurred.emit("Point selection mode is not active.")
            return

        if self._point_selection_collection.get_count() == 0:
            self.error_occurred.emit("No points selected. Please select at least one point.")
            return

        if self._background_remover is None:
            self.error_occurred.emit("Background remover not initialized")
            return

        # Don't start new operation if one is already in progress
        if self._background_removal_thread is not None and self._background_removal_thread.isRunning():
            return

        # Save current image state to operation history before applying operation
        import copy
        current_state = ImageModel(
            width=self._image_model.width,
            height=self._image_model.height,
            pixel_data=self._image_model.pixel_data.copy(),
            original_pixel_data=self._image_model.original_pixel_data.copy(),
            format=self._image_model.format,
            has_alpha=self._image_model.has_alpha,
        )
        self._operation_history.add_operation("remove_background", current_state)
        self.operation_history_changed.emit()

        # Convert points to SAM prompts
        prompts = self._point_selection_collection.to_sam_prompts()

        # Create worker and thread for background processing
        worker = BackgroundRemovalWorker(self._background_remover, self._image_model, prompts=prompts)
        thread = QThread(self)  # Set controller as parent for automatic cleanup
        worker.moveToThread(thread)

        # Connect signals
        thread.started.connect(worker.process)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_thread_finished)
        worker.result_ready.connect(self._on_background_removal_complete)
        worker.error_occurred.connect(self._on_background_removal_error)

        # Store references
        self._background_removal_thread = thread
        self._background_removal_worker = worker

        # Exit point selection mode and clear points
        self.exit_point_selection_mode()

        # Emit processing started signal
        self.processing_started.emit()

        # Start thread
        thread.start()

    def remove_background(self) -> None:
        """
        Remove background from current image using BackgroundRemover service.

        Uses QThread worker to maintain UI responsiveness during processing.
        This method is for automatic background removal (no prompts).

        Emits:
            image_updated: When background removal is complete
            error_occurred: If background removal fails
        """
        if self._image_model is None:
            self.error_occurred.emit("No image to process. Please load an image first.")
            return

        if self._background_remover is None:
            self.error_occurred.emit("Background remover not initialized")
            return

        # Don't start new operation if one is already in progress
        if self._background_removal_thread is not None and self._background_removal_thread.isRunning():
            return

        # Create worker and thread for background processing (no prompts)
        worker = BackgroundRemovalWorker(self._background_remover, self._image_model)
        thread = QThread(self)  # Set controller as parent for automatic cleanup
        worker.moveToThread(thread)

        # Connect signals
        thread.started.connect(worker.process)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_thread_finished)
        worker.result_ready.connect(self._on_background_removal_complete)
        worker.error_occurred.connect(self._on_background_removal_error)

        # Store references
        self._background_removal_thread = thread
        self._background_removal_worker = worker

        # Emit processing started signal
        self.processing_started.emit()

        # Start thread
        thread.start()

    def _on_thread_finished(self) -> None:
        """Handle thread finished signal - cleanup references."""
        self._background_removal_thread = None
        self._background_removal_worker = None

    def wait_for_background_removal(self, timeout: int = 5000) -> bool:
        """
        Wait for background removal thread to finish.

        Args:
            timeout: Maximum time to wait in milliseconds (default 5000ms)

        Returns:
            True if thread finished, False if timeout
        """
        if self._background_removal_thread is not None and self._background_removal_thread.isRunning():
            return self._background_removal_thread.wait(timeout)
        return True

    def _on_background_removal_complete(self, processed_image: ImageModel) -> None:
        """Handle background removal completion.

        Args:
            processed_image: ImageModel with background removed
        """
        # Update model (preserve original_pixel_data)
        self._image_model = ImageModel(
            width=processed_image.width,
            height=processed_image.height,
            pixel_data=processed_image.pixel_data,
            original_pixel_data=self._image_model.original_pixel_data.copy() if self._image_model else processed_image.original_pixel_data.copy(),
            format=processed_image.format,
            has_alpha=processed_image.has_alpha,
        )

        # Update statistics
        self._update_statistics()

        # Emit signals
        self.image_updated.emit(self._image_model)
        if self._statistics:
            self.statistics_updated.emit(self._statistics)

        # Emit processing finished signal
        self.processing_finished.emit()

    def _on_background_removal_error(self, error_message: str) -> None:
        """Handle background removal error.

        Args:
            error_message: Error message to display
        """
        self.error_occurred.emit(error_message)

        # Emit processing finished signal
        self.processing_finished.emit()

    def undo_operation(self) -> None:
        """
        Undo the last complex operation by restoring the previous image state.

        Restores the image to its state before the last operation and reapplies
        any slider-based changes (pixelization/color reduction) that were
        applied before that operation.

        Emits:
            image_updated: When undo is complete
            operation_history_changed: When history changes
            error_occurred: If undo fails or no operations to undo
        """
        if not self._operation_history.can_undo():
            self.error_occurred.emit("No operations to undo.")
            return

        if self._image_model is None:
            self.error_occurred.emit("No image loaded.")
            return

        # Get and remove the last operation from history
        entry = self._operation_history.pop_last_operation()
        if entry is None:
            self.error_occurred.emit("No operations to undo.")
            return

        # Restore the image state from the history entry
        restored_image = ImageModel(
            width=entry.image_state.width,
            height=entry.image_state.height,
            pixel_data=entry.image_state.pixel_data.copy(),
            original_pixel_data=entry.image_state.original_pixel_data.copy(),
            format=entry.image_state.format,
            has_alpha=entry.image_state.has_alpha,
        )

        # Reapply slider-based changes (pixelization and color reduction)
        # These are preserved and reapplied after undo
        if self._pixelizer is not None and self._settings_model.pixelization.is_enabled:
            pixel_size = self._settings_model.pixelization.pixel_size
            restored_image = self._pixelizer.pixelize(restored_image, pixel_size)

        if (
            self._color_reducer is not None
            and self._settings_model.color_reduction.is_enabled
        ):
            sensitivity = self._settings_model.color_reduction.sensitivity
            restored_image = self._color_reducer.reduce_colors(restored_image, sensitivity)

        # Update the image model
        self._image_model = ImageModel(
            width=restored_image.width,
            height=restored_image.height,
            pixel_data=restored_image.pixel_data,
            original_pixel_data=restored_image.original_pixel_data.copy(),
            format=restored_image.format,
            has_alpha=restored_image.has_alpha,
        )

        # Update statistics
        self._update_statistics()

        # Emit signals
        self.image_updated.emit(self._image_model)
        if self._statistics:
            self.statistics_updated.emit(self._statistics)
        self.operation_history_changed.emit()

    def clear_history(self) -> None:
        """Clear operation history.

        Emits:
            operation_history_changed: When history is cleared
        """
        self._operation_history.clear()
        self.operation_history_changed.emit()


class BackgroundRemovalWorker(QObject):
    """Worker for background removal processing in QThread."""

    result_ready = Signal(ImageModel)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(
        self,
        background_remover: "BackgroundRemover",
        image: ImageModel,
        prompts: Optional[list] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        """
        Initialize background removal worker.

        Args:
            background_remover: BackgroundRemover service instance
            image: ImageModel to process
            prompts: Optional SAM prompts for point-based removal
            parent: Parent QObject
        """
        super().__init__(parent)
        self._background_remover = background_remover
        self._image = image
        self._prompts = prompts

    def process(self) -> None:
        """Process background removal in worker thread."""
        try:
            processed_image = self._background_remover.remove_background(self._image, prompts=self._prompts)
            self.result_ready.emit(processed_image)
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "user_message"):
                error_msg = e.user_message
            self.error_occurred.emit(error_msg)
        finally:
            self.finished.emit()

