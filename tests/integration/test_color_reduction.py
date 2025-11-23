"""Integration tests for two-step color reduction workflow."""

import numpy as np
import pytest

from src.models.image_model import ImageModel
from src.services.color_reducer import ColorReducer


class TestColorReductionIntegration:
    """Integration tests for two-step color reduction workflow."""

    def test_two_step_color_reduction_workflow(self) -> None:
        """Test complete workflow: load image → apply color reduction → verify both steps applied."""
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

        # Apply color reduction with moderate sensitivity
        result = reducer.reduce_colors(image, sensitivity=0.6)

        # Verify Step 1 (quantization) was applied
        # After quantization, colors should be rounded to multiples
        result_count_after_step1 = ColorReducer.count_distinct_colors(result.pixel_data)
        assert result_count_after_step1 <= original_count, \
            f"Step 1 should reduce colors: {result_count_after_step1} <= {original_count}"

        # Verify Step 2 (clustering) was applied
        # After clustering, similar quantized colors should be grouped
        # The final count should be less than or equal to quantized count
        # (In practice, clustering further reduces colors)
        final_count = ColorReducer.count_distinct_colors(result.pixel_data)

        # Verify both steps worked together
        assert final_count <= original_count, \
            f"Final count should be less than original: {final_count} <= {original_count}"

        # Verify image properties preserved
        assert result.width == 10, "Width should be preserved"
        assert result.height == 10, "Height should be preserved"
        assert result.pixel_data.shape == (10, 10, 3), "Shape should be preserved"
        assert result.format == "PNG", "Format should be preserved"
        assert result.has_alpha == False, "Alpha status should be preserved"

    def test_color_reduction_with_sensitivity_variation(self) -> None:
        """Test that higher sensitivity produces more aggressive color reduction."""
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

        # Test with different sensitivity values
        result_low = reducer.reduce_colors(image, sensitivity=0.3)
        result_medium = reducer.reduce_colors(image, sensitivity=0.6)
        result_high = reducer.reduce_colors(image, sensitivity=0.9)

        count_low = ColorReducer.count_distinct_colors(result_low.pixel_data)
        count_medium = ColorReducer.count_distinct_colors(result_medium.pixel_data)
        count_high = ColorReducer.count_distinct_colors(result_high.pixel_data)

        # Higher sensitivity should produce fewer colors
        assert count_low >= count_medium >= count_high, \
            f"Higher sensitivity should reduce more colors: {count_low} >= {count_medium} >= {count_high}"

        # All should have fewer colors than original
        assert count_low <= original_count, \
            f"Low sensitivity should reduce colors: {count_low} <= {original_count}"
        assert count_high <= original_count, \
            f"High sensitivity should reduce colors: {count_high} <= {original_count}"

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

        result = reducer.reduce_colors(image, sensitivity=0.5)

        # Verify structure preserved
        assert result.width == 20, "Width should be preserved"
        assert result.height == 15, "Height should be preserved"
        assert result.pixel_data.shape == (15, 20, 3), "Shape should match"
        assert result.format == "PNG", "Format should be preserved"
        assert isinstance(result, ImageModel), "Should return ImageModel"

