"""Image saving service for saving processed images to PNG files."""

from pathlib import Path

import numpy as np
from PIL import Image as PILImage

from src.models.image_model import ImageModel
from src.services import ImageSaveError


class ImageSaver:
    """Service for saving processed images to PNG files."""

    def save_image(self, image: ImageModel, file_path: str) -> None:
        """
        Save processed image to PNG file.

        Args:
            image: ImageModel with processed pixel_data
            file_path: Full path where PNG file should be saved

        Raises:
            ValueError: If image is None or invalid
            ImageSaveError: If file cannot be written (permissions, disk full, etc.)
        """
        if image is None:
            raise ValueError("Image cannot be None")

        if image.pixel_data is None:
            raise ValueError("Image pixel_data cannot be None")

        # Validate and prepare file path
        path = Path(file_path)

        # Add .png extension if missing
        if path.suffix.lower() != ".png":
            path = path.with_suffix(".png")
            file_path = str(path)

        # Validate parent directory exists and is writable
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise ImageSaveError(
                    f"Cannot create directory: {str(e)}",
                    "Invalid file path. Please choose a valid location.",
                ) from e

        # Check if directory is writable
        if not parent_dir.is_dir() or not parent_dir.exists():
            raise ImageSaveError(
                f"Invalid directory: {parent_dir}",
                "Invalid file path. Please choose a valid location.",
            )

        try:
            # Convert NumPy array to PIL Image
            pixel_data = image.pixel_data

            # Ensure contiguous array
            pixel_data = np.ascontiguousarray(pixel_data, dtype=np.uint8)

            # Create PIL Image
            if image.has_alpha:
                pil_image = PILImage.fromarray(pixel_data, mode="RGBA")
            else:
                pil_image = PILImage.fromarray(pixel_data, mode="RGB")

            # Save as PNG
            pil_image.save(file_path, format="PNG")

        except PermissionError as e:
            raise ImageSaveError(
                f"Permission denied: {str(e)}",
                "Permission denied. Please choose a different location or check file permissions.",
            ) from e
        except OSError as e:
            # Handle disk full and other OS errors
            error_msg = str(e).lower()
            if "no space" in error_msg or "disk full" in error_msg:
                raise ImageSaveError(
                    f"Disk full: {str(e)}",
                    "Disk is full. Please free up space and try again.",
                ) from e
            raise ImageSaveError(
                f"Failed to save image: {str(e)}",
                "Failed to save image. Please try again.",
            ) from e
        except Exception as e:
            raise ImageSaveError(
                f"Unexpected error saving image: {str(e)}",
                "Failed to save image. Please try again.",
            ) from e

