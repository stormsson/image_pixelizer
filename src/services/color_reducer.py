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
        """
        Optimized K-Means: Finds centers using a downsampled image, 
        then applies palette to full image in chunks.
        """
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

        # --- STEP 1: TRAIN (Find Centers using Downsampled Data) ---
        # K-Means is slow on large images. We resize to a thumbnail to find
        # the dominant colors. This is 99% as accurate but 100x faster.
        max_train_dim = 200
        scale = min(1.0, max_train_dim / max(height, width))
        
        if scale < 1.0:
            small_width = int(width * scale)
            small_height = int(height * scale)
            # Use INTER_AREA for better color averaging during downscaling
            small_img = cv2.resize(rgb_data, (small_width, small_height), interpolation=cv2.INTER_AREA)
            train_pixels = small_img.reshape((-1, 3))
        else:
            train_pixels = rgb_data.reshape((-1, 3))

        train_pixels = np.float32(train_pixels)

        # Use robust criteria (100 iterations) because training data is now small/fast
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)
        
        try:
            # Use PP_CENTERS (High Quality)
            _, _, centers = cv2.kmeans(
                train_pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS
            )
        except Exception as e:
            print(f"K-Means training failed: {e}")
            return self._clone_image(image, pixel_data)

        # --- STEP 2: APPLY (Quantize Full Image) ---
        centers = np.float32(centers)
        flat_pixels = rgb_data.reshape((-1, 3)).astype(np.float32)
        n_pixels = flat_pixels.shape[0]
        
        # We need to find the nearest center for every pixel.
        # Calculating (N_pixels x K_centers) distance matrix is RAM heavy.
        # We process in chunks to stay CPU cache/RAM friendly.
        labels = np.zeros(n_pixels, dtype=np.int32)
        chunk_size = 4096  # Process 4096 pixels at a time
        
        # Pre-calculate sum of squares for centers to speed up Euclidean distance
        # formula: ||a - b||^2 = ||a||^2 + ||b||^2 - 2*a.b
        centers_sq_norm = np.sum(centers**2, axis=1) 

        for i in range(0, n_pixels, chunk_size):
            # Get chunk
            end = min(i + chunk_size, n_pixels)
            chunk = flat_pixels[i:end]
            
            # Vectorized Distance Calculation (Broadcasting)
            # dist = ||pixel||^2 + ||center||^2 - 2 * pixel . center
            # We only need the min, so we can ignore ||pixel||^2 part as it's constant for comparison
            
            # Dot product: (chunk_size, 3) @ (3, k) -> (chunk_size, k)
            term1 = -2 * np.matmul(chunk, centers.T)
            
            # Add centers squared norm
            dists = term1 + centers_sq_norm
            
            # Find nearest center index
            labels[i:end] = np.argmin(dists, axis=1)

        # Convert centers to uint8 for final image
        centers_uint8 = np.uint8(centers)
        
        # Map labels to colors
        quantized_flat = centers_uint8[labels]
        quantized_rgb = quantized_flat.reshape((height, width, 3))

        # --- STEP 3: HANDLE ALPHA ---
        if has_alpha:
            # Threshold Alpha
            alpha_binary = np.where(alpha_data >= 128, 255, 0).astype(np.uint8)
            
            # Optional: Mask RGB
            mask = alpha_binary == 255
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