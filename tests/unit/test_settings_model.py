"""Unit tests for SettingsModel, PixelizationSettings, and ColorReductionSettings."""

import pytest

from src.models.settings_model import (
    SettingsModel,
    PixelizationSettings,
    ColorReductionSettings,
)


class TestPixelizationSettings:
    """Tests for PixelizationSettings class."""

    def test_create_default_settings(self) -> None:
        """Test creating PixelizationSettings with default values."""
        settings = PixelizationSettings()

        assert settings.pixel_size == 1
        assert settings.is_enabled is False

    def test_create_custom_settings(self) -> None:
        """Test creating PixelizationSettings with custom values."""
        settings = PixelizationSettings(pixel_size=10, is_enabled=True)

        assert settings.pixel_size == 10
        assert settings.is_enabled is True

    def test_validation_accepts_minimum_pixel_size(self) -> None:
        """Test that pixel_size=1 is accepted (minimum value)."""
        settings = PixelizationSettings(pixel_size=1)
        assert settings.pixel_size == 1

    def test_validation_accepts_maximum_pixel_size(self) -> None:
        """Test that pixel_size=50 is accepted (maximum value)."""
        settings = PixelizationSettings(pixel_size=50)
        assert settings.pixel_size == 50

    def test_validation_rejects_zero_pixel_size(self) -> None:
        """Test that pixel_size=0 is rejected."""
        with pytest.raises(ValueError, match="pixel_size must be >= 1"):
            PixelizationSettings(pixel_size=0)

    def test_validation_rejects_negative_pixel_size(self) -> None:
        """Test that negative pixel_size is rejected."""
        with pytest.raises(ValueError, match="pixel_size must be >= 1"):
            PixelizationSettings(pixel_size=-1)

    def test_validation_rejects_excessive_pixel_size(self) -> None:
        """Test that pixel_size > 50 is rejected."""
        with pytest.raises(ValueError, match="pixel_size should not exceed 50"):
            PixelizationSettings(pixel_size=51)

    def test_toggle_enabled(self) -> None:
        """Test toggling is_enabled flag."""
        settings = PixelizationSettings()
        assert settings.is_enabled is False

        settings.is_enabled = True
        assert settings.is_enabled is True


class TestColorReductionSettings:
    """Tests for ColorReductionSettings class."""

    def test_create_default_settings(self) -> None:
        """Test creating ColorReductionSettings with default values."""
        settings = ColorReductionSettings()

        assert settings.bin_count is None
        assert settings.is_enabled is False

    def test_create_custom_settings_with_bin_count(self) -> None:
        """Test creating ColorReductionSettings with bin_count."""
        settings = ColorReductionSettings(bin_count=16)

        assert settings.bin_count == 16
        assert settings.is_enabled is True  # Auto-enabled when bin_count is set

    def test_create_custom_settings_with_none(self) -> None:
        """Test creating ColorReductionSettings with None bin_count."""
        settings = ColorReductionSettings(bin_count=None)

        assert settings.bin_count is None
        assert settings.is_enabled is False  # Auto-disabled when bin_count is None

    def test_validation_accepts_valid_bin_counts(self) -> None:
        """Test that all valid bin counts are accepted."""
        valid_bin_counts = [4, 8, 16, 32, 64, 128, 256]
        for bin_count in valid_bin_counts:
            settings = ColorReductionSettings(bin_count=bin_count)
            assert settings.bin_count == bin_count
            assert settings.is_enabled is True

    def test_validation_accepts_none(self) -> None:
        """Test that bin_count=None is accepted."""
        settings = ColorReductionSettings(bin_count=None)
        assert settings.bin_count is None
        assert settings.is_enabled is False

    def test_validation_rejects_invalid_bin_count(self) -> None:
        """Test that invalid bin_count values are rejected."""
        invalid_values = [0, 1, 2, 3, 5, 10, 20, 100, 512]
        for invalid_value in invalid_values:
            with pytest.raises(ValueError, match="bin_count must be one of"):
                ColorReductionSettings(bin_count=invalid_value)

    def test_validation_rejects_negative_bin_count(self) -> None:
        """Test that negative bin_count is rejected."""
        with pytest.raises(ValueError, match="bin_count must be one of"):
            ColorReductionSettings(bin_count=-1)

    def test_is_enabled_auto_set_with_bin_count(self) -> None:
        """Test that is_enabled is automatically set based on bin_count."""
        # None bin_count -> disabled
        settings = ColorReductionSettings(bin_count=None)
        assert settings.is_enabled is False

        # Valid bin_count -> enabled
        settings = ColorReductionSettings(bin_count=16)
        assert settings.is_enabled is True

    def test_setting_bin_count_updates_is_enabled(self) -> None:
        """Test that setting bin_count updates is_enabled."""
        settings = ColorReductionSettings()
        assert settings.is_enabled is False

        settings.bin_count = 32
        assert settings.is_enabled is True

        settings.bin_count = None
        assert settings.is_enabled is False


class TestSettingsModel:
    """Tests for SettingsModel class."""

    def test_create_default_settings_model(self) -> None:
        """Test creating SettingsModel with default values."""
        settings = SettingsModel()

        assert isinstance(settings.pixelization, PixelizationSettings)
        assert isinstance(settings.color_reduction, ColorReductionSettings)
        assert settings.pixelization.pixel_size == 1
        assert settings.color_reduction.bin_count is None

    def test_modify_pixelization_settings(self) -> None:
        """Test modifying pixelization settings through model."""
        settings = SettingsModel()
        settings.pixelization.pixel_size = 15
        settings.pixelization.is_enabled = True

        assert settings.pixelization.pixel_size == 15
        assert settings.pixelization.is_enabled is True

    def test_modify_color_reduction_settings(self) -> None:
        """Test modifying color reduction settings through model."""
        settings = SettingsModel()
        settings.color_reduction.bin_count = 64

        assert settings.color_reduction.bin_count == 64
        assert settings.color_reduction.is_enabled is True  # Auto-enabled

    def test_independent_settings(self) -> None:
        """Test that pixelization and color reduction settings are independent."""
        settings = SettingsModel()

        # Modify one, verify other unchanged
        settings.pixelization.pixel_size = 20
        assert settings.pixelization.pixel_size == 20
        assert settings.color_reduction.bin_count is None  # Unchanged

        settings.color_reduction.bin_count = 128
        assert settings.color_reduction.bin_count == 128
        assert settings.pixelization.pixel_size == 20  # Unchanged

