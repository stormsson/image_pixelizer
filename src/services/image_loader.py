"""Image loading and validation service."""

from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image as PILImage

from src.models.image_model import ImageModel
from src.services import ImageLoadError, ImageValidationError


class ImageLoader:
    """Loads and validates image files from file system."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    MAX_DIMENSION = 2000

    def validate_image_format(self, file_path: str) -> bool:
        """
        Validate that file is a supported image format.

        Args:
            file_path: Path to image file

        Returns:
            True if format is supported (JPEG, PNG, GIF, BMP)

        Raises:
            ImageValidationError: If format not supported
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in self.SUPPORTED_FORMATS:
            raise ImageValidationError(
                f"Unsupported file format: {suffix}",
                "Unsupported image format. Please use JPEG, PNG, GIF, BMP, or WebP.",
            )

        return True

    def validate_image_size(self, image: ImageModel) -> bool:
        """
        Validate image dimensions are within limits.

        Args:
            image: Image entity to validate

        Returns:
            True if dimensions <= 2000x2000px

        Raises:
            ImageValidationError: If dimensions exceed limit
        """
        if image.width > self.MAX_DIMENSION or image.height > self.MAX_DIMENSION:
            raise ImageValidationError(
                f"Image dimensions {image.width}x{image.height} exceed maximum",
                "Image size exceeds maximum of 2000x2000 pixels. Please resize the image.",
            )

        return True

    def load_image(self, file_path: str) -> ImageModel:
        """
        Load image from file path.

        Args:
            file_path: Path to image file

        Returns:
            Image entity with loaded pixel data

        Raises:
            ImageLoadError: If file doesn't exist or is corrupted
            ImageValidationError: If file format not supported or size exceeds limit
        """
        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            raise ImageLoadError(
                f"File not found: {file_path}",
                "The selected file could not be found. Please check the file path.",
            )

        # Validate format
        self.validate_image_format(file_path)

        try:
            # Load image using Pillow
            pil_image = PILImage.open(file_path)
            # Ensure image is fully loaded (important for JPEG and other formats)
            pil_image.load()

            # Convert to RGB/RGBA if needed
            if pil_image.mode == "RGBA":
                has_alpha = True
            elif pil_image.mode == "RGB":
                has_alpha = False
                pil_image = pil_image.convert("RGB")
            else:
                # Convert other modes to RGB
                has_alpha = False
                pil_image = pil_image.convert("RGB")

            # Convert to NumPy array
            # First convert PIL Image to NumPy array, then ensure it's contiguous
            # This fixes stride/alignment issues with JPEG, WebP, and other formats
            pixel_array = np.array(pil_image, dtype=np.uint8)
            pixel_array = np.ascontiguousarray(pixel_array)

            # Create ImageModel
            image = ImageModel(
                width=pil_image.width,
                height=pil_image.height,
                pixel_data=pixel_array.copy(),
                original_pixel_data=pixel_array.copy(),
                format=pil_image.format or "UNKNOWN",
                has_alpha=has_alpha,
            )

            # Validate size
            self.validate_image_size(image)

            return image

        except PILImage.UnidentifiedImageError as e:
            raise ImageLoadError(
                f"Corrupted or unreadable image: {file_path}",
                "The image file appears to be corrupted or unreadable. Please try a different file.",
            ) from e
        except Exception as e:
            if isinstance(e, (ImageLoadError, ImageValidationError)):
                raise
            raise ImageLoadError(
                f"Error loading image: {str(e)}",
                "The image file appears to be corrupted or unreadable. Please try a different file.",
            ) from e

