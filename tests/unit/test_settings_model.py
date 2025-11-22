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

        assert settings.sensitivity == 0.0
        assert settings.is_enabled is False

    def test_create_custom_settings(self) -> None:
        """Test creating ColorReductionSettings with custom values."""
        settings = ColorReductionSettings(sensitivity=0.5, is_enabled=True)

        assert settings.sensitivity == 0.5
        assert settings.is_enabled is True

    def test_validation_accepts_minimum_sensitivity(self) -> None:
        """Test that sensitivity=0.0 is accepted (minimum value)."""
        settings = ColorReductionSettings(sensitivity=0.0)
        assert settings.sensitivity == 0.0

    def test_validation_accepts_maximum_sensitivity(self) -> None:
        """Test that sensitivity=1.0 is accepted (maximum value)."""
        settings = ColorReductionSettings(sensitivity=1.0)
        assert settings.sensitivity == 1.0

    def test_validation_accepts_mid_range_sensitivity(self) -> None:
        """Test that sensitivity=0.5 is accepted."""
        settings = ColorReductionSettings(sensitivity=0.5)
        assert settings.sensitivity == 0.5

    def test_validation_rejects_negative_sensitivity(self) -> None:
        """Test that negative sensitivity is rejected."""
        with pytest.raises(ValueError, match="sensitivity must be between 0.0 and 1.0"):
            ColorReductionSettings(sensitivity=-0.1)

    def test_validation_rejects_excessive_sensitivity(self) -> None:
        """Test that sensitivity > 1.0 is rejected."""
        with pytest.raises(ValueError, match="sensitivity must be between 0.0 and 1.0"):
            ColorReductionSettings(sensitivity=1.1)

    def test_toggle_enabled(self) -> None:
        """Test toggling is_enabled flag."""
        settings = ColorReductionSettings()
        assert settings.is_enabled is False

        settings.is_enabled = True
        assert settings.is_enabled is True


class TestSettingsModel:
    """Tests for SettingsModel class."""

    def test_create_default_settings_model(self) -> None:
        """Test creating SettingsModel with default values."""
        settings = SettingsModel()

        assert isinstance(settings.pixelization, PixelizationSettings)
        assert isinstance(settings.color_reduction, ColorReductionSettings)
        assert settings.pixelization.pixel_size == 1
        assert settings.color_reduction.sensitivity == 0.0

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
        settings.color_reduction.sensitivity = 0.75
        settings.color_reduction.is_enabled = True

        assert settings.color_reduction.sensitivity == 0.75
        assert settings.color_reduction.is_enabled is True

    def test_independent_settings(self) -> None:
        """Test that pixelization and color reduction settings are independent."""
        settings = SettingsModel()

        # Modify one, verify other unchanged
        settings.pixelization.pixel_size = 20
        assert settings.pixelization.pixel_size == 20
        assert settings.color_reduction.sensitivity == 0.0  # Unchanged

        settings.color_reduction.sensitivity = 0.8
        assert settings.color_reduction.sensitivity == 0.8
        assert settings.pixelization.pixel_size == 20  # Unchanged

