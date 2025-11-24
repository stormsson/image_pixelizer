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
        Reduce number of distinct colors using two-step process.

        This method implements a two-step color reduction pipeline:

        **Step 1 (Quantization)**: Rounds each color channel to the nearest multiple
        of a quantization step, controlled by sensitivity. This makes nearby pixels
        have similar colors by reducing color precision.

        **Step 2 (Global Palette Clustering)**: Identifies all distinct colors in the
        quantized image, groups similar colors using a Euclidean distance threshold
        (also controlled by sensitivity), and replaces each group with a weighted
        average color (weighted by pixel count). This further reduces the color
        palette by merging visually similar colors.

        Both steps are controlled by the sensitivity parameter:
        - Higher sensitivity = larger quantization step (Step 1) and larger distance
          threshold (Step 2) = more aggressive color reduction
        - Lower sensitivity = smaller quantization step and threshold = less aggressive
          reduction, preserving more color detail
        - sensitivity=0.0 skips both steps and returns the original image unchanged

        Args:
            image: ImageModel to process
            sensitivity: Color reduction intensity (0.0 to 1.0)
                        - 0.0: No reduction (returns original image)
                        - 0.5: Moderate reduction
                        - 1.0: Maximum reduction (most aggressive)

        Returns:
            New ImageModel with reduced color palette

        Raises:
            ValueError: If sensitivity not in valid range [0.0, 1.0]
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
        # Use rounding instead of floor division to avoid darkening bias
        quantized_rgb = np.round(rgb_data.astype(np.float32) / quantization_step) * quantization_step

        # Ensure values stay in valid range [0, 255]
        quantized_rgb = np.clip(quantized_rgb, 0, 255).astype(np.uint8)

        # Reconstruct pixel data after Step 1 (quantization)
        if has_alpha:
            quantized_result = np.concatenate([quantized_rgb, alpha_data], axis=2)
        else:
            quantized_result = quantized_rgb

        # Step 2: Global palette clustering
        # Apply palette clustering to further reduce colors by grouping similar quantized colors
        clustered_result = self._apply_palette_clustering(quantized_result, sensitivity, has_alpha)

        return ImageModel(
            width=image.width,
            height=image.height,
            pixel_data=clustered_result,
            original_pixel_data=image.original_pixel_data.copy(),
            format=image.format,
            has_alpha=image.has_alpha,
        )

    def _calculate_distance_threshold(self, sensitivity: float) -> float:
        """
        Calculate color distance threshold from sensitivity parameter.

        Maps sensitivity (0.0 to 1.0) to distance threshold for color grouping.
        Higher sensitivity produces larger threshold (more aggressive grouping).

        Args:
            sensitivity: Sensitivity parameter (0.0 to 1.0)

        Returns:
            Distance threshold in RGB space (0.0 to max_distance)
        """
        # Map sensitivity to distance threshold
        # sensitivity 0.0 -> threshold 0.0 (no grouping)
        # sensitivity 1.0 -> threshold ~441.67 (max Euclidean distance in RGB: sqrt(255^2 + 255^2 + 255^2))
        # Use linear mapping for simplicity
        max_distance = np.sqrt(255.0 ** 2 + 255.0 ** 2 + 255.0 ** 2)  # ~441.67
        return sensitivity * max_distance

    def _calculate_color_distance(self, color1: np.ndarray, color2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two colors in RGB space.

        Args:
            color1: First color as numpy array (3 or 4 channels, only RGB used)
            color2: Second color as numpy array (3 or 4 channels, only RGB used)

        Returns:
            Euclidean distance in RGB space
        """
        # Extract RGB channels (first 3 channels)
        rgb1 = color1[:3].astype(np.float32)
        rgb2 = color2[:3].astype(np.float32)

        # Calculate Euclidean distance
        distance = np.sqrt(np.sum((rgb1 - rgb2) ** 2))
        return float(distance)

    def _identify_distinct_colors(self, image: np.ndarray) -> dict[tuple[int, ...], int]:
        """
        Identify all distinct colors in image and count pixel frequency for each.

        Args:
            image: NumPy array of shape (height, width, channels)

        Returns:
            Dictionary mapping color tuple to pixel count
        """
        height, width, channels = image.shape
        pixels = image.reshape(-1, channels)

        # Count frequency of each color
        color_counts: dict[tuple[int, ...], int] = {}
        for pixel in pixels:
            color_tuple = tuple(pixel)
            color_counts[color_tuple] = color_counts.get(color_tuple, 0) + 1

        return color_counts

    def _group_similar_colors(
        self, colors: dict[tuple[int, ...], int], threshold: float
    ) -> list[dict[tuple[int, ...], int]]:
        """
        Group similar colors within distance threshold using greedy clustering.

        Args:
            colors: Dictionary mapping color tuple to pixel count
            threshold: Maximum distance for colors to be considered similar

        Returns:
            List of color groups, where each group is a dict mapping color tuple to pixel count
        """
        if not colors:
            return []

        # Convert color tuples to numpy arrays for distance calculation
        color_list = list(colors.keys())
        color_arrays = [np.array(color, dtype=np.uint8) for color in color_list]

        groups: list[dict[tuple[int, ...], int]] = []
        used_colors = set()

        # Greedy clustering: for each unused color, create a group with all similar colors
        for i, color_tuple in enumerate(color_list):
            if color_tuple in used_colors:
                continue

            # Start new group with this color
            group: dict[tuple[int, ...], int] = {color_tuple: colors[color_tuple]}
            used_colors.add(color_tuple)

            # Find all similar colors within threshold
            for j, other_tuple in enumerate(color_list):
                if other_tuple in used_colors:
                    continue

                distance = self._calculate_color_distance(color_arrays[i], color_arrays[j])
                if distance <= threshold:
                    group[other_tuple] = colors[other_tuple]
                    used_colors.add(other_tuple)

            groups.append(group)

        return groups

    def _calculate_weighted_average_color(
        self, color_group: dict[tuple[int, ...], int]
    ) -> np.ndarray:
        """
        Calculate weighted average color for a group of similar colors.

        Weighted by pixel count - colors appearing more often have more influence.

        Args:
            color_group: Dictionary mapping color tuple to pixel count

        Returns:
            Average color as numpy array (3 channels for RGB)
        """
        if not color_group:
            return np.array([0, 0, 0], dtype=np.uint8)

        total_pixels = sum(color_group.values())
        if total_pixels == 0:
            return np.array([0, 0, 0], dtype=np.uint8)

        # Calculate weighted sum for each RGB channel
        weighted_sum = np.zeros(3, dtype=np.float32)
        for color_tuple, count in color_group.items():
            # Extract RGB channels (first 3)
            rgb = np.array(color_tuple[:3], dtype=np.float32)
            weight = count / total_pixels
            weighted_sum += rgb * weight

        # Round and clip to valid range
        average = np.round(weighted_sum).astype(np.int32)
        average = np.clip(average, 0, 255).astype(np.uint8)

        return average

    def _apply_palette_clustering(
        self, image: np.ndarray, sensitivity: float, has_alpha: bool
    ) -> np.ndarray:
        """
        Apply Step 2: Global palette clustering to reduce colors further.

        Identifies distinct colors, groups similar colors within threshold,
        and replaces each group with weighted average color.

        Args:
            image: NumPy array after Step 1 quantization (height, width, channels)
            sensitivity: Sensitivity parameter (0.0 to 1.0) controlling threshold
            has_alpha: Whether image has alpha channel

        Returns:
            Processed image with clustered colors
        """
        height, width, channels = image.shape

        # Separate RGB and alpha channels
        if has_alpha:
            rgb_data = image[:, :, :3]
            alpha_data = image[:, :, 3:4]
        else:
            rgb_data = image
            alpha_data = None

        # Calculate distance threshold from sensitivity
        threshold = self._calculate_distance_threshold(sensitivity)

        # If threshold is 0, no clustering needed
        if threshold <= 0.0:
            return image.copy()

        # Step 2.1: Identify distinct colors and their frequencies
        color_palette = self._identify_distinct_colors(rgb_data)

        # Step 2.2: Group similar colors within threshold
        color_groups = self._group_similar_colors(color_palette, threshold)

        # Step 2.3: Calculate weighted average for each group
        group_averages: dict[tuple[int, ...], np.ndarray] = {}
        for group in color_groups:
            average_color = self._calculate_weighted_average_color(group)
            # Map all colors in group to their average
            for color_tuple in group.keys():
                group_averages[color_tuple] = average_color

        # Step 2.4: Replace colors in image with group averages (vectorized)
        result_rgb = rgb_data.copy()
        
        # Create mapping from color tuples to average colors
        # Use vectorized approach: reshape to pixels, map colors, reshape back
        pixels = rgb_data.reshape(-1, 3)
        pixel_tuples = [tuple(p) for p in pixels]
        
        # Create replacement array
        replacements = np.array([
            group_averages.get(tuple(p), p) for p in pixels
        ], dtype=np.uint8)
        
        result_rgb = replacements.reshape(height, width, 3)

        # Reconstruct with alpha channel if present
        if has_alpha:
            result = np.concatenate([result_rgb, alpha_data], axis=2)
        else:
            result = result_rgb

        return result

