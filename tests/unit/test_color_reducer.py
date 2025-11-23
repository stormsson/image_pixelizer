"""Unit tests for ColorReducer service."""

import numpy as np
import pytest

from src.models.image_model import ImageModel
from src.services.color_reducer import ColorReducer


class TestColorReducer:
    """Tests for ColorReducer service."""

    def test_reduce_colors_basic(self) -> None:
        """Test basic color reduction with moderate sensitivity."""
        reducer = ColorReducer()

        # Create image with 4 distinct colors
        pixel_data = np.zeros((4, 4, 3), dtype=np.uint8)
        pixel_data[:2, :2] = [255, 0, 0]  # Red
        pixel_data[:2, 2:] = [0, 255, 0]  # Green
        pixel_data[2:, :2] = [0, 0, 255]  # Blue
        pixel_data[2:, 2:] = [255, 255, 0]  # Yellow

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, sensitivity=0.5)

        assert isinstance(result, ImageModel)
        assert result.width == 4
        assert result.height == 4
        assert result.pixel_data.shape == (4, 4, 3)
        assert result.format == "PNG"
        assert result.has_alpha == False

    def test_reduce_colors_sensitivity_zero(self) -> None:
        """Test color reduction with sensitivity=0.0 (no reduction)."""
        reducer = ColorReducer()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [100, 150, 200]

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, sensitivity=0.0)

        # With sensitivity 0, should return original image
        assert np.array_equal(result.pixel_data, pixel_data)

    def test_reduce_colors_sensitivity_one(self) -> None:
        """Test color reduction with sensitivity=1.0 (maximum reduction)."""
        reducer = ColorReducer()

        # Create image with many similar colors
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        for i in range(10):
            for j in range(10):
                pixel_data[i, j] = [i * 25, j * 25, (i + j) * 12]

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, sensitivity=1.0)

        # Should have fewer distinct colors than original
        original_colors = ColorReducer.count_distinct_colors(pixel_data)
        result_colors = ColorReducer.count_distinct_colors(result.pixel_data)
        assert result_colors <= original_colors

    def test_reduce_colors_rgba_image(self) -> None:
        """Test color reduction with RGBA image (preserves alpha)."""
        reducer = ColorReducer()

        pixel_data = np.zeros((4, 4, 4), dtype=np.uint8)
        pixel_data[:, :, :3] = [255, 0, 0]  # Red RGB
        pixel_data[:, :, 3] = 255  # Full alpha

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        result = reducer.reduce_colors(image, sensitivity=0.5)

        assert result.has_alpha == True
        assert result.pixel_data.shape == (4, 4, 4)
        # Alpha channel should be preserved
        assert np.all(result.pixel_data[:, :, 3] == 255)

    def test_reduce_colors_invalid_sensitivity(self) -> None:
        """Test color reduction with invalid sensitivity values."""
        reducer = ColorReducer()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        with pytest.raises(ValueError, match="sensitivity must be between 0.0 and 1.0"):
            reducer.reduce_colors(image, sensitivity=-0.1)

        with pytest.raises(ValueError, match="sensitivity must be between 0.0 and 1.0"):
            reducer.reduce_colors(image, sensitivity=1.1)

    def test_reduce_colors_creates_new_array(self) -> None:
        """Test that color reduction creates a new array (immutability)."""
        reducer = ColorReducer()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [100, 150, 200]

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, sensitivity=0.5)

        # Should be a new array, not the same reference
        assert result.pixel_data is not pixel_data
        assert result.pixel_data is not image.pixel_data

    def test_reduce_colors_reduces_color_count(self) -> None:
        """Test that color reduction actually reduces distinct color count."""
        reducer = ColorReducer()

        # Create image with many similar colors (gradient)
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
        result = reducer.reduce_colors(image, sensitivity=0.7)
        result_count = ColorReducer.count_distinct_colors(result.pixel_data)

        # Should have fewer or equal colors
        assert result_count <= original_count
        # With sensitivity 0.7, should have significantly fewer colors
        assert result_count < original_count

    def test_reduce_colors_higher_sensitivity_more_reduction(self) -> None:
        """Test that higher sensitivity produces more color reduction."""
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

        result_low = reducer.reduce_colors(image, sensitivity=0.3)
        result_high = reducer.reduce_colors(image, sensitivity=0.8)

        count_low = ColorReducer.count_distinct_colors(result_low.pixel_data)
        count_high = ColorReducer.count_distinct_colors(result_high.pixel_data)

        # Higher sensitivity should result in fewer colors
        assert count_high <= count_low

    def test_count_distinct_colors_basic(self) -> None:
        """Test counting distinct colors in image."""
        pixel_data = np.zeros((4, 4, 3), dtype=np.uint8)
        pixel_data[:2, :2] = [255, 0, 0]  # Red
        pixel_data[:2, 2:] = [0, 255, 0]  # Green
        pixel_data[2:, :2] = [0, 0, 255]  # Blue
        pixel_data[2:, 2:] = [255, 255, 0]  # Yellow

        count = ColorReducer.count_distinct_colors(pixel_data)
        assert count == 4

    def test_count_distinct_colors_uniform(self) -> None:
        """Test counting distinct colors in uniform image."""
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [100, 150, 200]

        count = ColorReducer.count_distinct_colors(pixel_data)
        assert count == 1

    def test_count_distinct_colors_rgba(self) -> None:
        """Test counting distinct colors in RGBA image."""
        pixel_data = np.zeros((4, 4, 4), dtype=np.uint8)
        pixel_data[:2, :2, :3] = [255, 0, 0]  # Red
        pixel_data[:2, :2, 3] = 255  # Alpha
        pixel_data[2:, 2:, :3] = [0, 255, 0]  # Green
        pixel_data[2:, 2:, 3] = 128  # Different alpha
        # Remaining pixels are [0, 0, 0, 0] (black with alpha 0)

        count = ColorReducer.count_distinct_colors(pixel_data)
        # Should count RGBA tuples: red+alpha255, green+alpha128, and black+alpha0
        assert count == 3

    def test_count_distinct_colors_empty(self) -> None:
        """Test counting distinct colors in empty image."""
        pixel_data = np.zeros((0, 0, 3), dtype=np.uint8)

        count = ColorReducer.count_distinct_colors(pixel_data)
        assert count == 0

    def test_reduce_colors_preserves_brightness(self) -> None:
        """Test that color reduction uses rounding (not floor division) to preserve brightness."""
        reducer = ColorReducer()

        # Create image with values that demonstrate rounding vs floor division difference
        # Test with step=32: 150/32 = 4.6875 -> rounds to 5 -> 5*32 = 160 (rounding)
        # With floor: 150//32 = 4 -> 4*32 = 128 (darker)
        pixel_data = np.zeros((2, 1, 3), dtype=np.uint8)
        pixel_data[0, 0] = [150, 150, 150]  # Should round to 160, not 128
        pixel_data[1, 0] = [200, 200, 200]  # Should round to 192 (same for both)

        image = ImageModel(
            width=1,
            height=2,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Use sensitivity that creates step=32
        # sensitivity = (32 - 1) / 63 = 0.492...
        result = reducer.reduce_colors(image, sensitivity=0.492)

        # Verify rounding behavior: 150 should round UP to 160, not DOWN to 128
        # With rounding: round(150/32) * 32 = round(4.6875) * 32 = 5 * 32 = 160
        # With floor: (150//32) * 32 = 4 * 32 = 128
        rounded_value = result.pixel_data[0, 0, 0]
        assert rounded_value >= 150, f"Rounding should preserve or increase brightness, got {rounded_value}"
        assert rounded_value != 128, "Should not use floor division (would give 128)"
        
        # Verify that the average brightness is better preserved
        original_avg = np.mean(pixel_data)
        result_avg = np.mean(result.pixel_data)
        # With rounding, the average should be closer to original
        brightness_difference = abs(result_avg - original_avg)
        # Floor division would give average ~144, rounding gives ~176 (closer to 150)
        assert brightness_difference < 30, f"Brightness should be preserved, difference: {brightness_difference}"

    # Tests for Step 2: Global Palette Clustering (FR-018 to FR-022)

    def test_step2_color_distance_calculation(self) -> None:
        """Test Step 2 color distance calculation (Euclidean distance in RGB space)."""
        reducer = ColorReducer()

        # Test Euclidean distance calculation
        color1 = np.array([255, 0, 0], dtype=np.uint8)  # Red
        color2 = np.array([0, 255, 0], dtype=np.uint8)  # Green
        color3 = np.array([255, 0, 0], dtype=np.uint8)  # Red (same as color1)

        # Distance between red and green should be sqrt((255-0)^2 + (0-255)^2 + (0-0)^2) = sqrt(130050) ≈ 360.6
        distance = reducer._calculate_color_distance(color1, color2)
        expected_distance = np.sqrt((255 - 0) ** 2 + (0 - 255) ** 2 + (0 - 0) ** 2)
        assert abs(distance - expected_distance) < 0.1, f"Expected distance ~{expected_distance}, got {distance}"

        # Distance between same colors should be 0
        distance_same = reducer._calculate_color_distance(color1, color3)
        assert distance_same == 0.0, f"Same colors should have distance 0, got {distance_same}"

    def test_step2_distance_threshold_mapping(self) -> None:
        """Test Step 2 distance threshold mapping from sensitivity."""
        reducer = ColorReducer()

        # Test threshold increases with sensitivity
        threshold_low = reducer._calculate_distance_threshold(0.0)
        threshold_mid = reducer._calculate_distance_threshold(0.5)
        threshold_high = reducer._calculate_distance_threshold(1.0)

        # Higher sensitivity should produce larger threshold
        assert threshold_low < threshold_mid < threshold_high, \
            f"Threshold should increase with sensitivity: {threshold_low} < {threshold_mid} < {threshold_high}"

        # Threshold should be non-negative
        assert threshold_low >= 0, f"Threshold should be non-negative, got {threshold_low}"
        assert threshold_high > 0, f"High sensitivity should produce positive threshold, got {threshold_high}"

    def test_step2_color_grouping(self) -> None:
        """Test Step 2 color grouping (group similar colors within threshold)."""
        reducer = ColorReducer()

        # Create a palette with similar colors
        colors = {
            (255, 0, 0): 10,  # Red - 10 pixels
            (250, 5, 0): 5,   # Similar red - 5 pixels (distance ~7.07)
            (0, 255, 0): 8,   # Green - 8 pixels
            (5, 250, 0): 3,   # Similar green - 3 pixels (distance ~7.07)
            (0, 0, 255): 12,  # Blue - 12 pixels
        }

        # With threshold of 10, reds should group together, greens should group together, blue stays alone
        groups = reducer._group_similar_colors(colors, threshold=10.0)

        # Should have 3 groups: red group, green group, blue group
        assert len(groups) == 3, f"Expected 3 groups, got {len(groups)}"

        # Verify groups contain correct colors
        group_colors = [set(group.keys()) for group in groups]
        red_group = next((g for g in group_colors if (255, 0, 0) in g), None)
        green_group = next((g for g in group_colors if (0, 255, 0) in g), None)
        blue_group = next((g for g in group_colors if (0, 0, 255) in g), None)

        assert red_group is not None, "Red group should exist"
        assert green_group is not None, "Green group should exist"
        assert blue_group is not None, "Blue group should exist"
        assert len(red_group) == 2, f"Red group should have 2 colors, got {len(red_group)}"
        assert len(green_group) == 2, f"Green group should have 2 colors, got {len(green_group)}"
        assert len(blue_group) == 1, f"Blue group should have 1 color, got {len(blue_group)}"

    def test_step2_color_grouping_no_similar_colors(self) -> None:
        """Test Step 2 color grouping with no similar colors (edge case)."""
        reducer = ColorReducer()

        # Create palette with very different colors
        colors = {
            (255, 0, 0): 10,  # Red
            (0, 255, 0): 8,   # Green
            (0, 0, 255): 12,  # Blue
        }

        # With very small threshold, no colors should group
        groups = reducer._group_similar_colors(colors, threshold=1.0)

        # Should have 3 separate groups (one per color)
        assert len(groups) == 3, f"Expected 3 separate groups, got {len(groups)}"

    def test_step2_color_grouping_all_similar(self) -> None:
        """Test Step 2 color grouping with all colors similar (edge case)."""
        reducer = ColorReducer()

        # Create palette with very similar colors
        colors = {
            (100, 100, 100): 10,
            (101, 101, 101): 5,
            (102, 102, 102): 8,
        }

        # With large threshold, all colors should group together
        groups = reducer._group_similar_colors(colors, threshold=10.0)

        # Should have 1 group containing all colors
        assert len(groups) == 1, f"Expected 1 group, got {len(groups)}"
        assert len(groups[0]) == 3, f"Group should contain all 3 colors, got {len(groups[0])}"

    def test_step2_weighted_average_calculation(self) -> None:
        """Test Step 2 weighted average calculation (weighted by pixel count)."""
        reducer = ColorReducer()

        # Create color group with different frequencies
        color_group = {
            (255, 0, 0): 10,  # Red - 10 pixels
            (250, 5, 0): 5,   # Similar red - 5 pixels
        }

        # Weighted average: (255*10 + 250*5) / 15 = 253.33...
        #                   (0*10 + 5*5) / 15 = 1.67...
        #                   (0*10 + 0*5) / 15 = 0
        average = reducer._calculate_weighted_average_color(color_group)

        assert len(average) == 3, f"Average should have 3 channels, got {len(average)}"
        # R channel: (255*10 + 250*5) / 15 ≈ 253.33
        assert abs(average[0] - 253.33) < 1.0, f"R channel should be ~253.33, got {average[0]}"
        # G channel: (0*10 + 5*5) / 15 ≈ 1.67
        assert abs(average[1] - 1.67) < 1.0, f"G channel should be ~1.67, got {average[1]}"
        # B channel: 0
        assert average[2] == 0, f"B channel should be 0, got {average[2]}"

    def test_step2_weighted_average_single_color(self) -> None:
        """Test Step 2 weighted average with single color."""
        reducer = ColorReducer()

        color_group = {
            (100, 150, 200): 5,
        }

        average = reducer._calculate_weighted_average_color(color_group)

        assert average[0] == 100, f"R channel should be 100, got {average[0]}"
        assert average[1] == 150, f"G channel should be 150, got {average[1]}"
        assert average[2] == 200, f"B channel should be 200, got {average[2]}"

    def test_step2_weighted_average_different_frequencies(self) -> None:
        """Test Step 2 weighted average with very different color frequencies."""
        reducer = ColorReducer()

        # One color appears much more often
        color_group = {
            (255, 0, 0): 100,  # Red - 100 pixels
            (250, 5, 0): 1,   # Similar red - 1 pixel
        }

        average = reducer._calculate_weighted_average_color(color_group)

        # Should be very close to the more frequent color
        assert abs(average[0] - 255) < 1.0, f"R channel should be close to 255, got {average[0]}"
        assert abs(average[1] - 0) < 1.0, f"G channel should be close to 0, got {average[1]}"

    def test_two_step_pipeline_execution(self) -> None:
        """Test two-step pipeline: Step 1 (quantization) then Step 2 (clustering)."""
        reducer = ColorReducer()

        # Create image with many similar colors
        pixel_data = np.zeros((4, 4, 3), dtype=np.uint8)
        pixel_data[0, 0] = [100, 100, 100]
        pixel_data[0, 1] = [101, 101, 101]
        pixel_data[0, 2] = [102, 102, 102]
        pixel_data[0, 3] = [103, 103, 103]
        pixel_data[1, :] = [200, 200, 200]
        pixel_data[2, :] = [201, 201, 201]
        pixel_data[3, :] = [202, 202, 202]

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # With sensitivity > 0, both steps should run
        result = reducer.reduce_colors(image, sensitivity=0.5)

        # Step 1 should quantize colors
        # Step 2 should further reduce by clustering similar quantized colors
        original_count = ColorReducer.count_distinct_colors(pixel_data)
        result_count = ColorReducer.count_distinct_colors(result.pixel_data)

        # Result should have fewer or equal colors
        assert result_count <= original_count, \
            f"Result should have fewer colors: {result_count} <= {original_count}"

    def test_two_step_pipeline_sensitivity_zero(self) -> None:
        """Test that sensitivity=0.0 skips both steps."""
        reducer = ColorReducer()

        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [100, 150, 200]

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = reducer.reduce_colors(image, sensitivity=0.0)

        # Should return original image unchanged
        assert np.array_equal(result.pixel_data, pixel_data), \
            "With sensitivity=0.0, image should be unchanged"

    def test_step2_with_alpha_channel(self) -> None:
        """Test Step 2 preserves alpha channel during clustering."""
        reducer = ColorReducer()

        # Create RGBA image with similar RGB colors but different alpha
        pixel_data = np.zeros((4, 4, 4), dtype=np.uint8)
        pixel_data[0, 0, :3] = [255, 0, 0]  # Red
        pixel_data[0, 0, 3] = 255  # Full alpha
        pixel_data[0, 1, :3] = [250, 5, 0]  # Similar red
        pixel_data[0, 1, 3] = 255  # Full alpha
        pixel_data[1, 0, :3] = [255, 0, 0]  # Red
        pixel_data[1, 0, 3] = 128  # Half alpha
        pixel_data[1, 1, :3] = [250, 5, 0]  # Similar red
        pixel_data[1, 1, 3] = 128  # Half alpha

        image = ImageModel(
            width=4,
            height=4,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=True,
        )

        result = reducer.reduce_colors(image, sensitivity=0.5)

        # Alpha channel should be preserved
        assert result.has_alpha == True, "Result should have alpha channel"
        assert result.pixel_data.shape == (4, 4, 4), "Result should be RGBA"

        # Alpha values should be preserved (clustering only affects RGB)
        # Pixels with alpha 255 should still have alpha 255
        assert np.all(result.pixel_data[0, :2, 3] == 255), "Alpha 255 should be preserved"
        assert np.all(result.pixel_data[1, :2, 3] == 128), "Alpha 128 should be preserved"

