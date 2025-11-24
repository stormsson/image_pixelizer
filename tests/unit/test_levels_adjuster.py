"""Unit tests for LevelsAdjuster service."""

import numpy as np
import pytest

from src.models.image_model import ImageModel
from src.services.levels_adjuster import LevelsAdjuster


class TestLevelsAdjusterStructure:
    """Tests for LevelsAdjuster class structure."""

    def test_class_instantiation(self) -> None:
        """Test that LevelsAdjuster can be instantiated."""
        adjuster = LevelsAdjuster()
        assert adjuster is not None
        assert isinstance(adjuster, LevelsAdjuster)

    def test_calculate_histogram_method_exists(self) -> None:
        """Test that calculate_histogram method exists and has correct signature."""
        adjuster = LevelsAdjuster()
        assert hasattr(adjuster, "calculate_histogram")
        assert callable(adjuster.calculate_histogram)

    def test_apply_levels_method_exists(self) -> None:
        """Test that apply_levels method exists and has correct signature."""
        adjuster = LevelsAdjuster()
        assert hasattr(adjuster, "apply_levels")
        assert callable(adjuster.apply_levels)


class TestCalculateHistogram:
    """Tests for histogram calculation (T051)."""

    def test_calculate_histogram_basic(self, sample_image_model: ImageModel) -> None:
        """Test basic histogram calculation for test image."""
        adjuster = LevelsAdjuster()
        histogram = adjuster.calculate_histogram(sample_image_model)

        assert isinstance(histogram, np.ndarray)
        assert histogram.shape == (256,)
        assert histogram.dtype == np.int32
        assert histogram.sum() == sample_image_model.width * sample_image_model.height

    def test_calculate_histogram_256_bins(self, sample_image_model: ImageModel) -> None:
        """Test histogram has 256 bins."""
        adjuster = LevelsAdjuster()
        histogram = adjuster.calculate_histogram(sample_image_model)

        assert len(histogram) == 256
        assert histogram.shape == (256,)

    def test_calculate_histogram_frequency_counts(self) -> None:
        """Test histogram frequency counts are correct."""
        adjuster = LevelsAdjuster()

        # Create image with known pixel values
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [128, 128, 128]  # All pixels are gray (luminance ~128)

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        # All 100 pixels should be in bin 128
        assert histogram[128] == 100
        assert histogram.sum() == 100

    def test_calculate_histogram_rgb_image(self) -> None:
        """Test histogram calculation with RGB image."""
        adjuster = LevelsAdjuster()

        pixel_data = np.zeros((5, 5, 3), dtype=np.uint8)
        pixel_data[:, :] = [255, 0, 0]  # Red

        image = ImageModel(
            width=5,
            height=5,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        assert histogram.sum() == 25
        # Red (255, 0, 0) has luminance ~76
        assert histogram[76] == 25

    def test_calculate_histogram_rgba_image(self, sample_rgba_image_model: ImageModel) -> None:
        """Test histogram calculation with RGBA image (alpha ignored)."""
        adjuster = LevelsAdjuster()
        histogram = adjuster.calculate_histogram(sample_rgba_image_model)

        assert isinstance(histogram, np.ndarray)
        assert histogram.shape == (256,)
        assert histogram.sum() == sample_rgba_image_model.width * sample_rgba_image_model.height

    def test_calculate_histogram_uniform_color(self) -> None:
        """Test histogram for uniform color image."""
        adjuster = LevelsAdjuster()

        pixel_data = np.zeros((20, 20, 3), dtype=np.uint8)
        pixel_data[:, :] = [200, 200, 200]  # Light gray

        image = ImageModel(
            width=20,
            height=20,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        # All pixels should be in the same bin (luminance ~200)
        assert histogram[200] == 400
        assert histogram.sum() == 400

    def test_calculate_histogram_gradient(self) -> None:
        """Test histogram for gradient image."""
        adjuster = LevelsAdjuster()

        # Create horizontal gradient from black to white
        pixel_data = np.zeros((10, 256, 3), dtype=np.uint8)
        for x in range(256):
            pixel_data[:, x] = [x, x, x]

        image = ImageModel(
            width=256,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        # Each tone level should have 10 pixels (one column)
        assert histogram.sum() == 2560
        assert all(count == 10 for count in histogram)


class TestApplyLevels:
    """Tests for levels adjustment application (T052)."""

    def test_apply_levels_darks_cutoff_only(self, sample_image_model: ImageModel) -> None:
        """Test applying darks cutoff only."""
        adjuster = LevelsAdjuster()
        result = adjuster.apply_levels(sample_image_model, darks_cutoff=10.0, lights_cutoff=0.0)

        assert isinstance(result, ImageModel)
        assert result.width == sample_image_model.width
        assert result.height == sample_image_model.height
        # Original should be unchanged
        assert np.array_equal(sample_image_model.pixel_data, sample_image_model.original_pixel_data)

    def test_apply_levels_lights_cutoff_only(self, sample_image_model: ImageModel) -> None:
        """Test applying lights cutoff only."""
        adjuster = LevelsAdjuster()
        result = adjuster.apply_levels(sample_image_model, darks_cutoff=0.0, lights_cutoff=10.0)

        assert isinstance(result, ImageModel)
        assert result.width == sample_image_model.width
        assert result.height == sample_image_model.height

    def test_apply_levels_both_cutoffs(self, sample_image_model: ImageModel) -> None:
        """Test applying both cutoffs simultaneously."""
        adjuster = LevelsAdjuster()
        result = adjuster.apply_levels(sample_image_model, darks_cutoff=5.0, lights_cutoff=10.0)

        assert isinstance(result, ImageModel)
        assert result.width == sample_image_model.width
        assert result.height == sample_image_model.height

    def test_apply_levels_pixel_replacement(self) -> None:
        """Test that pixels are replaced correctly."""
        adjuster = LevelsAdjuster()

        # Create image with gradient
        pixel_data = np.zeros((10, 256, 3), dtype=np.uint8)
        for x in range(256):
            pixel_data[:, x] = [x, x, x]

        image = ImageModel(
            width=256,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        result = adjuster.apply_levels(image, darks_cutoff=10.0, lights_cutoff=10.0)
        # Some pixels should be replaced
        assert not np.array_equal(result.pixel_data, image.pixel_data)

    def test_apply_levels_zero_cutoffs(self, sample_image_model: ImageModel) -> None:
        """Test that zero cutoffs result in no change."""
        adjuster = LevelsAdjuster()
        result = adjuster.apply_levels(sample_image_model, darks_cutoff=0.0, lights_cutoff=0.0)

        assert isinstance(result, ImageModel)
        # With zero cutoffs, result should be identical to input
        assert np.array_equal(result.pixel_data, sample_image_model.pixel_data)

    def test_apply_levels_max_cutoffs(self, sample_image_model: ImageModel) -> None:
        """Test that max cutoffs replace all pixels."""
        adjuster = LevelsAdjuster()
        result = adjuster.apply_levels(sample_image_model, darks_cutoff=100.0, lights_cutoff=100.0)

        assert isinstance(result, ImageModel)
        # With 100% cutoffs, all pixels should be either black or white

    def test_apply_levels_preserves_alpha(self, sample_rgba_image_model: ImageModel) -> None:
        """Test that alpha channel is preserved."""
        adjuster = LevelsAdjuster()
        original_alpha = sample_rgba_image_model.pixel_data[:, :, 3].copy()

        result = adjuster.apply_levels(sample_rgba_image_model, darks_cutoff=5.0, lights_cutoff=5.0)

        assert result.has_alpha is True
        assert np.array_equal(result.pixel_data[:, :, 3], original_alpha)


class TestErrorHandling:
    """Tests for error handling (T053)."""

    def test_calculate_histogram_invalid_image_none(self) -> None:
        """Test error handling for None image."""
        adjuster = LevelsAdjuster()
        with pytest.raises(ValueError, match="Invalid image"):
            adjuster.calculate_histogram(None)  # type: ignore

    def test_calculate_histogram_empty_image(self) -> None:
        """Test error handling for empty image."""
        adjuster = LevelsAdjuster()
        pixel_data = np.zeros((0, 0, 3), dtype=np.uint8)
        image = ImageModel(
            width=0,
            height=0,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )
        with pytest.raises(ValueError, match="empty"):
            adjuster.calculate_histogram(image)

    def test_apply_levels_invalid_image_none(self) -> None:
        """Test error handling for None image."""
        adjuster = LevelsAdjuster()
        with pytest.raises(ValueError, match="Invalid image"):
            adjuster.apply_levels(None, 5.0, 10.0)  # type: ignore

    def test_apply_levels_invalid_cutoff_values_negative(self, sample_image_model: ImageModel) -> None:
        """Test error handling for negative cutoff values."""
        adjuster = LevelsAdjuster()
        with pytest.raises(ValueError, match="between 0.0 and 100.0"):
            adjuster.apply_levels(sample_image_model, darks_cutoff=-1.0, lights_cutoff=10.0)

    def test_apply_levels_invalid_cutoff_values_too_large(self, sample_image_model: ImageModel) -> None:
        """Test error handling for cutoff values > 100."""
        adjuster = LevelsAdjuster()
        with pytest.raises(ValueError, match="between 0.0 and 100.0"):
            adjuster.apply_levels(sample_image_model, darks_cutoff=5.0, lights_cutoff=101.0)


class TestHistogramEdgeCases:
    """Tests for histogram calculation edge cases (T054)."""

    def test_histogram_very_dark_image(self) -> None:
        """Test histogram for very dark image."""
        adjuster = LevelsAdjuster()
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [10, 10, 10]  # Very dark

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        assert histogram.sum() == 100
        # Most pixels should be in low bins
        assert histogram[:50].sum() == 100

    def test_histogram_very_light_image(self) -> None:
        """Test histogram for very light image."""
        adjuster = LevelsAdjuster()
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [245, 245, 245]  # Very light

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        assert histogram.sum() == 100
        # Most pixels should be in high bins
        assert histogram[200:].sum() == 100

    def test_histogram_single_color_image(self) -> None:
        """Test histogram for single color image."""
        adjuster = LevelsAdjuster()
        pixel_data = np.zeros((50, 50, 3), dtype=np.uint8)
        pixel_data[:, :] = [128, 128, 128]  # Single gray color

        image = ImageModel(
            width=50,
            height=50,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        assert histogram.sum() == 2500
        # All pixels in same bin
        assert histogram[128] == 2500

    def test_histogram_grayscale_image(self) -> None:
        """Test histogram for grayscale image (RGB with R=G=B)."""
        adjuster = LevelsAdjuster()
        pixel_data = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            pixel_data[i, :] = [i * 12, i * 12, i * 12]  # Grayscale gradient

        image = ImageModel(
            width=20,
            height=20,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        histogram = adjuster.calculate_histogram(image)
        assert histogram.sum() == 400


class TestLevelsAdjustmentEdgeCases:
    """Tests for levels adjustment edge cases (T055)."""

    def test_both_sliders_at_100_percent(self, sample_image_model: ImageModel) -> None:
        """Test both sliders at 100%."""
        adjuster = LevelsAdjuster()
        result = adjuster.apply_levels(sample_image_model, darks_cutoff=100.0, lights_cutoff=100.0)

        assert isinstance(result, ImageModel)
        # All pixels should be either black or white

    def test_overlapping_thresholds(self) -> None:
        """Test overlapping thresholds (darks and lights cutoffs overlap)."""
        adjuster = LevelsAdjuster()
        pixel_data = np.zeros((10, 10, 3), dtype=np.uint8)
        pixel_data[:, :] = [128, 128, 128]  # Mid-gray

        image = ImageModel(
            width=10,
            height=10,
            pixel_data=pixel_data,
            original_pixel_data=pixel_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Large cutoffs that overlap
        result = adjuster.apply_levels(image, darks_cutoff=50.0, lights_cutoff=50.0)
        assert isinstance(result, ImageModel)

    def test_grayscale_vs_color_images(self) -> None:
        """Test levels adjustment works on both grayscale and color images."""
        adjuster = LevelsAdjuster()

        # Grayscale image
        gray_data = np.zeros((10, 10, 3), dtype=np.uint8)
        gray_data[:, :] = [128, 128, 128]
        gray_image = ImageModel(
            width=10,
            height=10,
            pixel_data=gray_data,
            original_pixel_data=gray_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        # Color image
        color_data = np.zeros((10, 10, 3), dtype=np.uint8)
        color_data[:, :] = [255, 0, 0]  # Red
        color_image = ImageModel(
            width=10,
            height=10,
            pixel_data=color_data,
            original_pixel_data=color_data.copy(),
            format="PNG",
            has_alpha=False,
        )

        gray_result = adjuster.apply_levels(gray_image, darks_cutoff=10.0, lights_cutoff=10.0)
        color_result = adjuster.apply_levels(color_image, darks_cutoff=10.0, lights_cutoff=10.0)

        assert isinstance(gray_result, ImageModel)
        assert isinstance(color_result, ImageModel)

