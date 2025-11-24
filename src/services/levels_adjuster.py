"""Image levels adjustment service for tonal distribution modification."""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from src.models.image_model import ImageModel
else:
    from src.models.image_model import ImageModel


class LevelsAdjuster:
    """Service for calculating histograms and applying levels adjustments to images.

    Provides stateless methods for histogram calculation and levels adjustment
    operations. Follows the same pattern as ColorReducer and Pixelizer services.
    """

    def calculate_histogram(self, image: "ImageModel") -> np.ndarray:
        """Calculate histogram of tonal distribution for an image.

        Args:
            image: Image to analyze. Must have valid pixel_data.

        Returns:
            Array of 256 integers representing frequency counts for each tone level
            (0-255). Shape: (256,). dtype: np.int32.

        Raises:
            ValueError: If image is None, pixel_data is invalid, or image is empty.

        Example:
            >>> adjuster = LevelsAdjuster()
            >>> histogram = adjuster.calculate_histogram(image_model)
            >>> # histogram[0] = count of pixels with tone level 0 (black)
            >>> # histogram[255] = count of pixels with tone level 255 (white)
        """
        if image is None:
            raise ValueError(
                "Invalid image: image cannot be None. Please provide a valid ImageModel instance."
            )

        if not hasattr(image, "pixel_data"):
            raise ValueError(
                "Invalid image: image does not have pixel_data attribute. "
                "Please provide a valid ImageModel instance."
            )

        if image.pixel_data.size == 0:
            raise ValueError(
                "Cannot calculate histogram for empty image. "
                "The image has no pixel data (width or height is 0)."
            )

        # Extract RGB channels (ignore alpha if present)
        rgb_data = image.pixel_data[:, :, :3]

        # Convert to grayscale using luminance formula: 0.299*R + 0.587*G + 0.114*B
        luminance = (
            0.299 * rgb_data[:, :, 0].astype(np.float32)
            + 0.587 * rgb_data[:, :, 1].astype(np.float32)
            + 0.114 * rgb_data[:, :, 2].astype(np.float32)
        )

        # Calculate histogram with 256 bins (one per tone level)
        histogram, _ = np.histogram(
            luminance.flatten(), bins=256, range=(0, 256)
        )

        # Return as int32 array
        return histogram.astype(np.int32)

    def apply_levels(
        self, image: "ImageModel", darks_cutoff: float, lights_cutoff: float
    ) -> "ImageModel":
        """Apply levels adjustment to image by clipping highlights and shadows.

        Args:
            image: Image to adjust. Must have valid pixel_data.
            darks_cutoff: Percentage of darkest pixels to replace with black (0.0-100.0).
                0.0 = no change, 100.0 = all pixels become black.
            lights_cutoff: Percentage of lightest pixels to replace with white (0.0-100.0).
                0.0 = no change, 100.0 = all pixels become white.

        Returns:
            New ImageModel instance with adjusted pixel_data. Original pixel_data is
            preserved in original_pixel_data. All other attributes (width, height,
            format, has_alpha) are copied from input.

        Raises:
            ValueError: If image is None, pixel_data is invalid, or cutoff values
                are not in [0.0, 100.0].

        Example:
            >>> adjuster = LevelsAdjuster()
            >>> # Replace darkest 5% with black, lightest 10% with white
            >>> adjusted_image = adjuster.apply_levels(image_model, darks_cutoff=5.0, lights_cutoff=10.0)
        """
        # Validate inputs with specific error messages
        if image is None:
            raise ValueError("Invalid image: image cannot be None. Please provide a valid ImageModel instance.")

        if not isinstance(darks_cutoff, (int, float)):
            raise ValueError(
                f"Invalid darks_cutoff: expected a number between 0.0 and 100.0, got {type(darks_cutoff).__name__}"
            )
        if darks_cutoff < 0.0:
            raise ValueError(
                f"Invalid darks_cutoff: value must be between 0.0 and 100.0, got {darks_cutoff}. "
                "Negative values are not allowed."
            )
        if darks_cutoff > 100.0:
            raise ValueError(
                f"Invalid darks_cutoff: value must be between 0.0 and 100.0, got {darks_cutoff}. "
                "Values above 100% are not allowed."
            )

        if not isinstance(lights_cutoff, (int, float)):
            raise ValueError(
                f"Invalid lights_cutoff: expected a number between 0.0 and 100.0, got {type(lights_cutoff).__name__}"
            )
        if lights_cutoff < 0.0:
            raise ValueError(
                f"Invalid lights_cutoff: value must be between 0.0 and 100.0, got {lights_cutoff}. "
                "Negative values are not allowed."
            )
        if lights_cutoff > 100.0:
            raise ValueError(
                f"Invalid lights_cutoff: value must be between 0.0 and 100.0, got {lights_cutoff}. "
                "Values above 100% are not allowed."
            )

        # If both cutoffs are 0, return unchanged image
        if darks_cutoff == 0.0 and lights_cutoff == 0.0:
            return ImageModel(
                width=image.width,
                height=image.height,
                pixel_data=image.pixel_data.copy(),
                original_pixel_data=image.original_pixel_data.copy(),
                format=image.format,
                has_alpha=image.has_alpha,
            )

        # Calculate histogram to find percentile thresholds
        histogram = self.calculate_histogram(image)

        # Calculate cumulative distribution
        cumulative = np.cumsum(histogram).astype(np.float64)
        total_pixels = cumulative[-1]

        if total_pixels == 0:
            # Empty image, return unchanged
            return ImageModel(
                width=image.width,
                height=image.height,
                pixel_data=image.pixel_data.copy(),
                original_pixel_data=image.original_pixel_data.copy(),
                format=image.format,
                has_alpha=image.has_alpha,
            )

        # Find percentile thresholds
        darks_threshold = 0
        lights_threshold = 255

        if darks_cutoff > 0.0:
            # Find tone level where darks_cutoff% of pixels are darker
            target_count = total_pixels * (darks_cutoff / 100.0)
            darks_threshold = np.searchsorted(cumulative, target_count, side="right")
            darks_threshold = min(darks_threshold, 255)

        if lights_cutoff > 0.0:
            # Find tone level where lights_cutoff% of pixels are lighter
            target_count = total_pixels * (1.0 - lights_cutoff / 100.0)
            lights_threshold = np.searchsorted(cumulative, target_count, side="left")
            lights_threshold = max(lights_threshold, 0)

        # Create copy of pixel data
        result_data = image.pixel_data.copy()

        # Extract RGB channels (use view to avoid copy if possible)
        rgb_data = result_data[:, :, :3]

        # Calculate luminance for each pixel using vectorized operations
        # Use float32 for better performance and memory efficiency
        r_channel = rgb_data[:, :, 0].astype(np.float32, copy=False)
        g_channel = rgb_data[:, :, 1].astype(np.float32, copy=False)
        b_channel = rgb_data[:, :, 2].astype(np.float32, copy=False)
        
        # Vectorized luminance calculation (single operation, no loops)
        luminance = 0.299 * r_channel + 0.587 * g_channel + 0.114 * b_channel

        # Apply darks cutoff: pixels with luminance <= threshold → black
        # Use boolean indexing for efficient vectorized assignment
        if darks_cutoff > 0.0:
            darks_mask = luminance <= darks_threshold
            # Direct assignment to avoid intermediate arrays
            rgb_data[darks_mask, 0] = 0
            rgb_data[darks_mask, 1] = 0
            rgb_data[darks_mask, 2] = 0

        # Apply lights cutoff: pixels with luminance >= threshold → white
        # Use boolean indexing for efficient vectorized assignment
        if lights_cutoff > 0.0:
            lights_mask = luminance >= lights_threshold
            # Direct assignment to avoid intermediate arrays
            rgb_data[lights_mask, 0] = 255
            rgb_data[lights_mask, 1] = 255
            rgb_data[lights_mask, 2] = 255

        # Alpha channel is already preserved in result_data (copied from original)

        # Create new ImageModel with adjusted data
        return ImageModel(
            width=image.width,
            height=image.height,
            pixel_data=result_data,
            original_pixel_data=image.original_pixel_data.copy(),
            format=image.format,
            has_alpha=image.has_alpha,
        )

