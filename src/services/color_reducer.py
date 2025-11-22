"""Color reduction service for reducing distinct colors in images."""

import numpy as np

from src.models.image_model import ImageModel


class ColorReducer:
    """Service for reducing distinct colors in images using color quantization."""

    @staticmethod
    def count_distinct_colors(image: np.ndarray) -> int:
        """
        Count number of distinct colors in image.

        Args:
            image: NumPy array of shape (height, width, channels)

        Returns:
            Number of unique RGB/RGBA color values
        """
        if image.size == 0:
            return 0

        # Reshape to (height * width, channels) to count unique colors
        pixels = image.reshape(-1, image.shape[2])
        # Convert to tuples for hashing
        unique_colors = len(set(tuple(p) for p in pixels))
        return unique_colors

    def reduce_colors(self, image: ImageModel, sensitivity: float) -> ImageModel:
        """
        Reduce number of distinct colors by merging similar colors.

        Args:
            image: ImageModel to process
            sensitivity: Color similarity threshold (0.0 to 1.0)
                        Higher = more aggressive merging = fewer colors

        Returns:
            New ImageModel with reduced color palette

        Raises:
            ValueError: If sensitivity not in valid range
            ValueError: If image array is invalid
        """
        if sensitivity < 0.0 or sensitivity > 1.0:
            raise ValueError("sensitivity must be between 0.0 and 1.0")

        # If sensitivity is 0, no color reduction needed
        if sensitivity == 0.0:
            return ImageModel(
                width=image.width,
                height=image.height,
                pixel_data=image.pixel_data.copy(),
                original_pixel_data=image.original_pixel_data.copy(),
                format=image.format,
                has_alpha=image.has_alpha,
            )

        pixel_data = image.pixel_data.copy()
        height, width, channels = pixel_data.shape

        # Calculate quantization step based on sensitivity
        # sensitivity 0.0 -> step 1 (no quantization)
        # sensitivity 1.0 -> step 255 (maximum quantization, all colors become one)
        # Use a non-linear mapping for better user experience
        # Map 0.0-1.0 to quantization steps 1-64 (more granular control)
        quantization_step = 1 + int(sensitivity * 63)

        # Separate RGB and alpha channels if present
        has_alpha = channels == 4
        if has_alpha:
            rgb_data = pixel_data[:, :, :3]
            alpha_data = pixel_data[:, :, 3:4]
        else:
            rgb_data = pixel_data
            alpha_data = None

        # Quantize RGB channels
        # Round each color channel to nearest multiple of quantization_step
        quantized_rgb = (rgb_data // quantization_step) * quantization_step

        # Ensure values stay in valid range [0, 255]
        quantized_rgb = np.clip(quantized_rgb, 0, 255).astype(np.uint8)

        # Reconstruct pixel data
        if has_alpha:
            result = np.concatenate([quantized_rgb, alpha_data], axis=2)
        else:
            result = quantized_rgb

        return ImageModel(
            width=image.width,
            height=image.height,
            pixel_data=result,
            original_pixel_data=image.original_pixel_data.copy(),
            format=image.format,
            has_alpha=image.has_alpha,
        )

