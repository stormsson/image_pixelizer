"""Main controller coordinating models, services, and views."""

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from src.models.image_model import ImageModel, ImageStatistics
from src.models.settings_model import SettingsModel

if TYPE_CHECKING:
    from src.services.color_reducer import ColorReducer
    from src.services.image_loader import ImageLoader
    from src.services.image_saver import ImageSaver
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

    def __init__(
        self,
        image_model: Optional[ImageModel] = None,
        settings_model: Optional[SettingsModel] = None,
        image_loader: Optional["ImageLoader"] = None,
        image_saver: Optional["ImageSaver"] = None,
        pixelizer: Optional["Pixelizer"] = None,
        color_reducer=None,  # ColorReducer - will be set later
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
        """
        super().__init__()
        self._image_model = image_model
        self._settings_model = settings_model or SettingsModel()
        self._image_loader = image_loader
        self._image_saver = image_saver
        self._pixelizer = pixelizer
        self._color_reducer = color_reducer
        self._statistics: Optional[ImageStatistics] = None

    @property
    def image_model(self) -> Optional[ImageModel]:
        """Get current image model.

        Returns:
            Current ImageModel instance or None if no image loaded.
        """
        return self._image_model

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

