import numpy as np
import cv2  # Required for K-Means

from src.models.image_model import ImageModel
from typing import Optional

class ColorReducer:
    """Service for reducing distinct colors in images using K-Means clustering."""

    @staticmethod
    def count_distinct_colors(image: np.ndarray) -> int:
        """Count number of distinct colors in image."""
        if image.size == 0:
            return 0
        
        # Reshape to list of pixels
        pixels = image.reshape(-1, image.shape[2])
        
        # FIX 1: Sanitize Transparent Pixels
        # If image has Alpha channel (4 channels)
        if image.shape[2] == 4:
            # We need to work on a copy to avoid modifying the actual image view in memory
            pixels = pixels.copy()
            
            # Find where Alpha is 0 (fully transparent)
            # and force RGB to 0 to ensure all invisible pixels count as 1 color
            alpha_channel = pixels[:, 3]
            pixels[alpha_channel == 0] = [0, 0, 0, 0]

        return len(np.unique(pixels, axis=0))

    def reduce_colors(
        self, 
        image: ImageModel, 
        k: Optional[int] = None
    ) -> ImageModel:
        """
        Reduce number of distinct colors in the image using K-Means clustering.

        Args:
            image: ImageModel to process.
            sensitivity: Float 0.0-1.0, controls number of colors (higher = fewer colors).
            k: (Optional) Specific number of colors for K-Means.
        """
        if k is None:
            return self._clone_image(image, image.pixel_data.copy())

        return self._reduce_via_kmeans(image, k)

    def _reduce_via_kmeans(self, image: ImageModel, k: Optional[int]) -> ImageModel:
        """Apply K-Means Clustering to reduce image to exactly K colors."""
        pixel_data = image.pixel_data.copy()
        height, width, channels = pixel_data.shape
        

        # Separate Alpha if exists
        has_alpha = channels == 4
        if has_alpha:
            rgb_data = pixel_data[:, :, :3]
            alpha_data = pixel_data[:, :, 3:4]
        else:
            rgb_data = pixel_data
            alpha_data = None

        # 1. Flatten the image to a list of pixels
        pixels = rgb_data.reshape((-1, 3))
        pixels = np.float32(pixels)

        # 2. Define K-Means criteria
        MAX_ITERATIONS_AMOUNT = 10
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, MAX_ITERATIONS_AMOUNT, 1.0)

        # 3. Apply K-Means
        try:
            _, labels, centers = cv2.kmeans(
                pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS # cv2.KMEANS_RANDOM_CENTERS
            )
        except Exception as e:
            print(f"K-Means failed: {e}")
            return self._clone_image(image, pixel_data)

        # 4. Convert centers back to uint8
        centers = np.uint8(centers)

        # 5. Map labels to center colors
        quantized_flat = centers[labels.flatten()]

        # 6. Reshape back to image dimensions
        quantized_rgb = quantized_flat.reshape((height, width, 3))

        # FIX 2: Handle Alpha Channel Reduction
        if has_alpha:
            # Create binary alpha (Threshold at 128)
            # This ensures 'smooth' edges become hard edges, reducing color count
            # and matching the "Pixel Art" aesthetic.
            alpha_binary = np.where(alpha_data >= 128, 255, 0).astype(np.uint8)
            
            # Optional: Ensure RGB is black/zero where Alpha is transparent
            # This cleans up "invisible noise"
            mask = alpha_binary == 255
            # Broadcast mask to 3 channels
            mask_rgb = np.repeat(mask, 3, axis=2)
            quantized_rgb = np.where(mask_rgb, quantized_rgb, 0)

            result_data = np.concatenate([quantized_rgb, alpha_binary], axis=2)
        else:
            result_data = quantized_rgb

        return self._clone_image(image, result_data)

    def _clone_image(self, original: ImageModel, new_data: np.ndarray) -> ImageModel:
        """Helper to create a new ImageModel maintaining original metadata."""
        return ImageModel(
            width=original.width,
            height=original.height,
            pixel_data=new_data,
            original_pixel_data=original.original_pixel_data.copy(),
            format=original.format,
            has_alpha=original.has_alpha,
        )