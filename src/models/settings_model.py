"""Settings models for pixelization and color reduction."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PixelizationSettings:
    """Configuration for pixelization effect.

    Attributes:
        pixel_size: Size of each pixel block (1-50). Value of 1 means no
            pixelization effect.
        is_enabled: Whether pixelization is currently enabled. Automatically
            set to True when pixel_size > 1.
    """

    pixel_size: int = 1
    is_enabled: bool = False

    def __post_init__(self) -> None:
        """Validate pixelization settings after initialization.

        Raises:
            ValueError: If pixel_size is outside valid range (1-50).
        """
        if self.pixel_size < 1:
            raise ValueError("pixel_size must be >= 1")
        if self.pixel_size > 50:
            raise ValueError("pixel_size should not exceed 50 for reasonable effects")


@dataclass
class ColorReductionSettings:
    """Configuration for color reduction effect.

    Attributes:
        bin_count: Number of color clusters for k-means clustering. Must be one of:
            None (disables color reduction), 4, 8, 16, 32, 64, 128, 256.
            Value of None means no color reduction.
        is_enabled: Whether color reduction is currently enabled. Automatically
            set to True when bin_count is not None.
    """

    bin_count: Optional[int] = None
    is_enabled: bool = False

    def __post_init__(self) -> None:
        """Validate color reduction settings after initialization.

        Raises:
            ValueError: If bin_count is not None and not a valid power of 2 (4-256).
        """
        # Auto-set is_enabled based on bin_count
        self.is_enabled = self.bin_count is not None
        
        # Validate bin_count if provided
        if self.bin_count is not None:
            valid_bin_counts = {4, 8, 16, 32, 64, 128, 256}
            if self.bin_count not in valid_bin_counts:
                raise ValueError(
                    f"bin_count must be one of {sorted(valid_bin_counts)} or None, "
                    f"got {self.bin_count}"
                )
    
    def __setattr__(self, name: str, value: object) -> None:
        """Override to keep is_enabled in sync with bin_count."""
        super().__setattr__(name, value)
        # If bin_count is being set, update is_enabled automatically
        if name == "bin_count":
            # Validate if setting a non-None value
            if value is not None:
                valid_bin_counts = {4, 8, 16, 32, 64, 128, 256}
                if value not in valid_bin_counts:
                    raise ValueError(
                        f"bin_count must be one of {sorted(valid_bin_counts)} or None, "
                        f"got {value}"
                    )
            # Auto-update is_enabled
            super().__setattr__("is_enabled", value is not None)


@dataclass
class SettingsModel:
    """Container for all application settings.

    This model holds configuration for all image processing operations,
    including pixelization and color reduction settings.

    Attributes:
        pixelization: Pixelization effect configuration.
        color_reduction: Color reduction effect configuration.
    """

    pixelization: PixelizationSettings
    color_reduction: ColorReductionSettings

    def __init__(self) -> None:
        """Initialize settings model with default values.

        Creates new instances of PixelizationSettings and ColorReductionSettings
        with default values (no effects enabled).
        """
        self.pixelization = PixelizationSettings()
        self.color_reduction = ColorReductionSettings()

