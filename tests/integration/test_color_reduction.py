"""Integration tests for color reduction workflow using K-Means clustering."""

import numpy as np
import pytest

from src.models.image_model import ImageModel
from src.services.color_reducer import ColorReducer


class TestColorReductionIntegration:
    """Integration tests for color reduction workflow using K-Means clustering."""

    def test_color_reduction_workflow(self) -> None:
        """Test complete workflow: load image → apply color reduction → verify K-Means applied."""
        reducer = ColorReducer()

        # Create image with many similar colors that should be reduced
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        for i in range(10):
            for j in range(10):
                # Create gradient with many similar colors
                pixel_data[i, j] = [i * 25, j * 25, (i + j) * 12]

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Count original distinct colors
        original_count = ColorReducer.count_distinct_colors(pixel_data)

        # Apply color reduction with k=16 colors
        result = reducer.reduce_colors(image, k=16)

        # Verify K-Means clustering was applied
        # After clustering, colors should be reduced to at most k colors
        final_count = ColorReducer.count_distinct_colors(result.pixel_data)

        # Verify color reduction worked
        assert final_count <= original_count, \
            f"Final count should be less than original: {final_count} <= {original_count}"
        assert final_count <= 16, \
            f"Should have at most 16 colors (k=16), got {final_count}"

        # Verify image properties preserved
        assert result.width == 10, "Width should be preserved"
        assert result.height == 10, "Height should be preserved"
        assert result.pixel_data.shape == (10, 10, 3), "Shape should be preserved"
        assert result.format == "PNG", "Format should be preserved"
        assert result.has_alpha == False, "Alpha status should be preserved"

    def test_color_reduction_with_k_variation(self) -> None:
        """Test that lower k values produce more aggressive color reduction."""
        reducer = ColorReducer()

        # Create image with many colors
        pixel_data = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            for j in range(20):
                pixel_data[i, j] = [i * 12, j * 12, (i + j) * 6]

        image = ImageModel(
            width=20,
            height=20,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        original_count = ColorReducer.count_distinct_colors(pixel_data)

        # Test with different k values
        result_high_k = reducer.reduce_colors(image, k=64)
        result_medium_k = reducer.reduce_colors(image, k=16)
        result_low_k = reducer.reduce_colors(image, k=4)

        count_high_k = ColorReducer.count_distinct_colors(result_high_k.pixel_data)
        count_medium_k = ColorReducer.count_distinct_colors(result_medium_k.pixel_data)
        count_low_k = ColorReducer.count_distinct_colors(result_low_k.pixel_data)

        # Lower k should produce fewer colors
        assert count_high_k >= count_medium_k >= count_low_k, \
            f"Lower k should reduce more colors: {count_high_k} >= {count_medium_k} >= {count_low_k}"

        # All should have fewer colors than original
        assert count_high_k <= original_count, \
            f"High k should reduce colors: {count_high_k} <= {original_count}"
        assert count_low_k <= original_count, \
            f"Low k should reduce colors: {count_low_k} <= {original_count}"
        
        # Verify k limits are respected (at most k distinct colors)
        assert count_high_k <= 64, f"Should have at most 64 colors, got {count_high_k}"
        assert count_medium_k <= 16, f"Should have at most 16 colors, got {count_medium_k}"
        assert count_low_k <= 4, f"Should have at most 4 colors, got {count_low_k}"

    def test_color_reduction_preserves_image_structure(self) -> None:
        """Test that color reduction preserves image structure and dimensions."""
        reducer = ColorReducer()

        # Create test image
        pixel_data = np.zeros((15, 20, 3), dtype=np.uint8)
        pixel_data[:, :] = [128, 128, 128]

        image = ImageModel(
            width=20,
            height=15,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, k=16)

        # Verify structure preserved
        assert result.width == 20, "Width should be preserved"
        assert result.height == 15, "Height should be preserved"
        assert result.pixel_data.shape == (15, 20, 3), "Shape should match"
        assert result.format == "PNG", "Format should be preserved"
        assert isinstance(result, ImageModel), "Should return ImageModel"

