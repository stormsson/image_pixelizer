import numpy as np
import cv2  # Required for K-Means

from src.models.image_model import ImageModel
from typing import Optional

class ColorReducer:
    """Service for reducing distinct colors in images using quantization or K-Means."""

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
        sensitivity: float = 0.5, 
        method: str = "kmeans",
        k: Optional[int] = None
    ) -> ImageModel:
        """
        Reduce number of distinct colors in the image.

        Args:
            image: ImageModel to process.
            sensitivity: Float 0.0-1.0.
            method: "quantize" (default) or "kmeans".
            k: (Optional) Specific number of colors for K-Means.
        """
        if sensitivity == 0.0 and k is None:
            return self._clone_image(image, image.pixel_data.copy())

        if method == "kmeans":
            return self._reduce_via_kmeans(image, sensitivity, k)
        else:
            return self._reduce_via_quantization(image, sensitivity)

    def _reduce_via_kmeans(self, image: ImageModel, sensitivity: float, k: Optional[int]) -> ImageModel:
        """Apply K-Means Clustering to reduce image to exactly K colors."""
        pixel_data = image.pixel_data.copy()
        height, width, channels = pixel_data.shape
        
        # Determine K (number of clusters)
        if k is None:
            if sensitivity <= 0:
                return self._clone_image(image, pixel_data)
            
            max_k = 256
            min_k = 8
            k = int(max_k - (sensitivity * (max_k - min_k)))
            k = max(min_k, k)

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
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

        # 3. Apply K-Means
        try:
            _, labels, centers = cv2.kmeans(
                pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
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

    def _reduce_via_quantization(self, image: ImageModel, sensitivity: float) -> ImageModel:
        """Original two-step quantization and greedy clustering process."""
        if sensitivity < 0.0 or sensitivity > 1.0:
            raise ValueError("sensitivity must be between 0.0 and 1.0")

        pixel_data = image.pixel_data.copy()
        channels = pixel_data.shape[2]

        # Calculate quantization step based on sensitivity
        quantization_step = 1 + int(sensitivity * 63)

        # Separate RGB and alpha
        has_alpha = channels == 4
        if has_alpha:
            rgb_data = pixel_data[:, :, :3]
            alpha_data = pixel_data[:, :, 3:4]
        else:
            rgb_data = pixel_data
            alpha_data = None

        # Step 1: Rounding Quantization on RGB
        quantized_rgb = np.round(rgb_data.astype(np.float32) / quantization_step) * quantization_step
        quantized_rgb = np.clip(quantized_rgb, 0, 255).astype(np.uint8)

        if has_alpha:
            # FIX 3: Also Quantize Alpha
            # Use a simpler threshold for alpha to keep edges clean, 
            # or quantize it using the same step if you want "posterized" transparency.
            # Usually for pixelizers, binary threshold is best:
            alpha_binary = np.where(alpha_data >= 128, 255, 0).astype(np.uint8)
            
            # Clean RGB where alpha is 0
            mask = alpha_binary == 255
            mask_rgb = np.repeat(mask, 3, axis=2)
            quantized_rgb = np.where(mask_rgb, quantized_rgb, 0)

            quantized_result = np.concatenate([quantized_rgb, alpha_binary], axis=2)
        else:
            quantized_result = quantized_rgb

        # Step 2: Global palette clustering
        # Note: We pass has_alpha=False to clustering here because we merged it manually 
        # and sanitized it above, effectively treating the image as a solid block 
        # or handling alpha simply.
        clustered_result = self._apply_palette_clustering(quantized_result, sensitivity, has_alpha)

        return self._clone_image(image, clustered_result)

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

    # -------------------------------------------------------------------------
    # EXISTING HELPER METHODS 
    # -------------------------------------------------------------------------

    def _calculate_distance_threshold(self, sensitivity: float) -> float:
        max_distance = np.sqrt(255.0 ** 2 + 255.0 ** 2 + 255.0 ** 2)
        return sensitivity * max_distance

    def _calculate_color_distance(self, color1: np.ndarray, color2: np.ndarray) -> float:
        rgb1 = color1[:3].astype(np.float32)
        rgb2 = color2[:3].astype(np.float32)
        return float(np.sqrt(np.sum((rgb1 - rgb2) ** 2)))

    def _identify_distinct_colors(self, image: np.ndarray) -> dict[tuple[int, ...], int]:
        height, width, channels = image.shape
        pixels = image.reshape(-1, channels)
        color_counts: dict[tuple[int, ...], int] = {}
        
        unique_pixels, counts = np.unique(pixels, axis=0, return_counts=True)
        for pixel, count in zip(unique_pixels, counts):
            color_counts[tuple(pixel)] = count
            
        return color_counts

    def _group_similar_colors(
        self, colors: dict[tuple[int, ...], int], threshold: float
    ) -> list[dict[tuple[int, ...], int]]:
        if not colors:
            return []
        color_list = list(colors.keys())
        color_arrays = np.array(color_list, dtype=np.float32) 
        
        groups = []
        used_indices = set()

        for i in range(len(color_list)):
            if i in used_indices:
                continue

            current_color = color_arrays[i]
            group = {color_list[i]: colors[color_list[i]]}
            used_indices.add(i)

            for j in range(i + 1, len(color_list)):
                if j in used_indices:
                    continue
                
                dist = np.linalg.norm(current_color - color_arrays[j])
                if dist <= threshold:
                    group[color_list[j]] = colors[color_list[j]]
                    used_indices.add(j)

            groups.append(group)
        return groups

    def _calculate_weighted_average_color(self, color_group: dict) -> np.ndarray:
        if not color_group:
            return np.array([0, 0, 0], dtype=np.uint8)
            
        colors = np.array([list(k) for k in color_group.keys()]) 
        counts = np.array(list(color_group.values())).reshape(-1, 1) 
        
        total_pixels = np.sum(counts)
        if total_pixels == 0: return np.array([0,0,0], dtype=np.uint8)
        
        weighted_sum = np.sum(colors * counts, axis=0)
        average = np.round(weighted_sum / total_pixels).astype(np.int32)
        return np.clip(average, 0, 255).astype(np.uint8)

    def _apply_palette_clustering(
        self, image: np.ndarray, sensitivity: float, has_alpha: bool
    ) -> np.ndarray:
        height, width, channels = image.shape
        
        if has_alpha:
            rgb_data = image[:, :, :3]
            alpha_data = image[:, :, 3:4]
        else:
            rgb_data = image
            alpha_data = None

        threshold = self._calculate_distance_threshold(sensitivity)
        if threshold <= 0.0:
            return image.copy()

        color_palette = self._identify_distinct_colors(rgb_data)
        
        if len(color_palette) > 2000: 
            print("Warning: Too many colors for greedy clustering. Skipping Step 2.")
            return image.copy()
            
        color_groups = self._group_similar_colors(color_palette, threshold)

        mapping = {}
        for group in color_groups:
            avg = self._calculate_weighted_average_color(group)
            for color_tuple in group.keys():
                mapping[color_tuple] = avg

        pixels = rgb_data.reshape(-1, 3)
        
        pixel_tuples = [tuple(p) for p in pixels]
        new_pixels = np.array([mapping.get(pt, pt) for pt in pixel_tuples], dtype=np.uint8)
        
        result_rgb = new_pixels.reshape(height, width, 3)

        if has_alpha:
            return np.concatenate([result_rgb, alpha_data], axis=2)
        return result_rgb